# 경쟁사 블로그 모니터링 설정

`config.md`와 같은 형식, 다른 대상 — 이건 우리 블로그가 아니라 **경쟁사** 블로그 목록입니다. `scripts/fetch_rss.py --config config_competitors.md`로 실행하면 이 파일을 읽습니다.

## 블로그 목록

`이름` 칸은 비워두거나 id를 그대로 적어도 됩니다 — 스크립트가 RSS에서 실제 블로그 제목을 읽어와 자동으로 채웁니다.

| id | 이름 |
|---|---|
| shmy3300 | shmy3300 |
| chofall2021 | chofall2021 |
| jjune0010 | jjune0010 |
| fallingrain90 | fallingrain90 |
| the_onecom90 | the_onecom90 |
| wldnjswlghks1 | wldnjswlghks1 |
| speed1867 | speed1867 |
| mamasky09 | mamasky09 |
| melody404 | melody404 |
| highhigh3022 | highhigh3022 |
| cjsuddl88 | cjsuddl88 |
| sayfree9 | sayfree9 |
| mksung0913 | mksung0913 |
| band1101 | band1101 |
| malice0404 | malice0404 |
| yuks76 | yuks76 |
| malice0926 | malice0926 |
| 7575aaa | 7575aaa |
| solluna8082 | solluna8082 |
| chlrhqnehdtks486 | chlrhqnehdtks486 |
| chlfactory | chlfactory |

## 관심 지역

`config.md`와 동일한 기준으로 맞춘다 — 우리 쪽과 경쟁사 쪽 코드/키워드가 어긋나면 두 대시보드를 나란히 비교하는 의미가 없다.

| 코드 | 표시 이름 | 매칭 키워드 |
|---|---|---|
| pt | 평택 | 평택 |
| as | 안성 | 안성 |
| ca | 천안·아산 | 천안,아산 |
| hs | 화성 | 화성 |
| os | 오산 | 오산 |
| yi | 용인 | 용인 |

## 기본 기준일

- 커버리지/우선순위: 5일
- 캘린더: 10일

## 마지막 Artifact URL

https://claude.ai/code/artifact/2d35938e-cdbb-4020-8559-918e1519c940
