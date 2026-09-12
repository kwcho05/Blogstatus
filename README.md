# Blogstatus — 네이버 블로그 포스팅 모니터링

공장·창고 임대를 중개하는 부동산업자가 운영하는 네이버 블로그 여러 개와 경쟁사 블로그들의 포스팅 현황을, 관심 지역 기준으로 모니터링하는 Claude 스킬입니다.

## 구성

- `SKILL.md` — Claude Code 스킬 정의 및 실행 지침
- `config.md` — 내 블로그 목록, 관심 지역, 기준일 설정 (원본 설정 파일)
- `config_competitors.md` — 경쟁사 블로그 설정
- `scripts/fetch_rss.py` — 네이버 블로그 RSS를 가져와 지역별로 분류하는 스크립트 (`curl_cffi`로 Safari TLS를 흉내내 봇 차단을 우회)
- `assets/dashboard_template.html` — 내 블로그용 대시보드 템플릿 (지역 커버리지, 다음 포스팅 우선순위, 캘린더, 상세 목록)
- `assets/competitor_dashboard_template.html` — 경쟁사용 대시보드 템플릿 (지역별 경쟁 강도, 캘린더, 상세 목록)

## 사용법

이 폴더를 Claude Code 스킬(`~/.claude/skills/naver-blog-monitor/`)로 설치하면 "블로그 현황 갱신해줘", "경쟁사 현황 갱신해줘" 같은 요청으로 실행됩니다. 자세한 절차는 `SKILL.md`를 참고하세요.

```bash
uv run --with curl_cffi python scripts/fetch_rss.py --out blog_data.json
```
