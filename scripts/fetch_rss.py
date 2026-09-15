#!/usr/bin/env python3
"""Fetch and parse RSS feeds for the user's Naver blogs, tag posts by target city,
and dump JSON ready to inject into assets/dashboard_template.html.

All the tunable stuff (blog list, target cities, default day windows) lives in
../config.md, not in this file -- edit that file, not this one, for routine
changes. This script only reads it.

Run with a Python that has curl_cffi. Easiest portable way:
    uv run --with curl_cffi python fetch_rss.py --out out.json

curl_cffi is required (not plain requests/urllib) because blog.naver.com and
rss.blog.naver.com sit behind bot detection that blocks a plain TLS fingerprint.
impersonate="safari" consistently gets a 200 with the real feed body.
"""
import argparse
import datetime
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path
import json

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.md"


def _section(text: str, heading: str) -> str:
    m = re.search(rf"^##\s*{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def _table_rows(section_text: str) -> list[list[str]]:
    lines = [l for l in section_text.splitlines() if l.strip().startswith("|")]
    if len(lines) < 2:
        return []
    rows = []
    for line in lines[2:]:  # skip header row + the |---|---| separator row
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    return rows


def parse_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"config.md not found at {path}. This skill reads blog list / target "
            f"cities / default day windows from config.md next to the scripts/ folder."
        )
    text = path.read_text(encoding="utf-8")

    blogs = [
        {"id": row[0], "handle": row[0], "name": row[1]}
        for row in _table_rows(_section(text, "블로그 목록"))
        if len(row) >= 2 and row[0]
    ]
    cities = []
    for row in _table_rows(_section(text, "관심 지역")):
        if len(row) < 2 or not row[0]:
            continue
        code, label = row[0], row[1]
        # 3번째 칸(매칭 키워드)이 있으면 그 목록으로 제목을 검사하고, 없으면 표시 이름 자체로
        # 검사한다. 두 지역을 한 카테고리로 묶고 싶을 때(예: 천안·아산) 여기에 "천안,아산"처럼
        # 콤마로 여러 키워드를 넣으면 된다 -- 표시는 하나로 합쳐지고, 매칭은 둘 다 걸린다.
        if len(row) >= 3 and row[2].strip():
            keywords = [k.strip() for k in row[2].split(",") if k.strip()]
        else:
            keywords = [label]
        cities.append({"code": code, "label": label, "keywords": keywords})

    defaults_text = _section(text, "기본 기준일")
    m_matrix = re.search(r"커버리지[^\d]*(\d+)\s*일", defaults_text)
    m_cal = re.search(r"캘린더[^\d]*(\d+)\s*일", defaults_text)
    matrix_days = int(m_matrix.group(1)) if m_matrix else 5
    calendar_days = int(m_cal.group(1)) if m_cal else 10

    url_text = _section(text, "마지막 Artifact URL")
    m_url = re.search(r"https?://\S+", url_text)
    artifact_url = m_url.group(0) if m_url else None

    if not blogs:
        raise ValueError(f"config.md의 '블로그 목록' 표에서 blogId를 하나도 못 읽었습니다: {path}")
    if not cities:
        raise ValueError(f"config.md의 '관심 지역' 표에서 지역을 하나도 못 읽었습니다: {path}")

    return {
        "blogs": blogs,
        "cities": cities,
        "matrix_days": matrix_days,
        "calendar_days": calendar_days,
        "artifact_url": artifact_url,
    }


def fetch_feed(blog_id: str) -> bytes:
    from curl_cffi import requests as cffi_requests
    resp = cffi_requests.get(
        f"https://rss.blog.naver.com/{blog_id}.xml", impersonate="safari", timeout=20
    )
    resp.raise_for_status()
    return resp.content


def classify(title: str, cities: list[dict]) -> list[str]:
    matched = [c["code"] for c in cities if any(kw in title for kw in c["keywords"])]
    return matched if matched else ["etc"]


def parse_feed(xml_bytes: bytes, blog_id: str, cutoff: datetime.date, cities: list[dict]):
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    channel_title = (channel.findtext("title") or "").strip()
    items = []
    for it in channel.findall("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").split("?")[0]
        pub_raw = it.findtext("pubDate")
        if not pub_raw:
            continue
        dt = parsedate_to_datetime(pub_raw)
        if dt.date() < cutoff:
            continue
        items.append(
            {
                "blog": blog_id,
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M"),
                "title": title,
                "link": link,
                "cities": classify(title, cities),
            }
        )
    return channel_title, items


def build_days(today: datetime.date, calendar_days: int):
    start = today - datetime.timedelta(days=calendar_days - 1)
    days = []
    d = start
    while d <= today:
        days.append({"iso": d.isoformat(), "md": d.strftime("%m/%d"), "wd": WEEKDAY_KO[d.weekday()]})
        d += datetime.timedelta(days=1)
    return days


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="설정 md 파일 경로")
    ap.add_argument("--matrix-days", type=int, default=None, help="기본값은 config.md의 '기본 기준일'을 따름")
    ap.add_argument("--calendar-days", type=int, default=None, help="기본값은 config.md의 '기본 기준일'을 따름")
    ap.add_argument("--out", default="blog_data.json")
    args = ap.parse_args()

    cfg = parse_config(Path(args.config))
    matrix_days = args.matrix_days if args.matrix_days is not None else cfg["matrix_days"]
    calendar_days = args.calendar_days if args.calendar_days is not None else cfg["calendar_days"]

    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=calendar_days - 1)

    all_posts = []
    errors = []
    for b in cfg["blogs"]:
        try:
            xml_bytes = fetch_feed(b["id"])
            channel_title, items = parse_feed(xml_bytes, b["id"], cutoff, cfg["cities"])
            # config.md's name column is a convenience label a human typed in; the
            # RSS channel title is the blog's real display name and is what the
            # dashboard should show. Prefer it whenever the feed actually has one
            # (e.g. competitor blogs where nobody bothered to type a name in config.md).
            if channel_title:
                b["name"] = channel_title
            all_posts.extend(items)
        except Exception as e:  # noqa: BLE001 - surface every blog's failure, don't stop the batch
            errors.append({"blog": b["id"], "error": str(e)})

    all_posts.sort(key=lambda p: p["date"] + p["time"], reverse=True)

    out = {
        "today": today.isoformat(),
        # 대시보드 헤더의 "수집 시각" 표시용 -- 같은 날 여러 번 갱신해도 언제 받아온
        # 데이터인지 화면에서 바로 보이게 한다.
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "matrix_window_days": matrix_days,
        "calendar_days": calendar_days,
        "blogs": cfg["blogs"],
        "cities": [{"code": c["code"], "label": c["label"]} for c in cfg["cities"]],
        "last_artifact_url": cfg["artifact_url"],
        "days": build_days(today, calendar_days),
        "posts": all_posts,
        "errors": errors,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # Keep console output ASCII-only: Windows consoles are frequently cp949 and
    # will throw UnicodeEncodeError on the Korean titles/names above.
    print(f"wrote {args.out}: {len(all_posts)} posts from {len(cfg['blogs'])} blogs, {len(errors)} errors")


if __name__ == "__main__":
    main()
