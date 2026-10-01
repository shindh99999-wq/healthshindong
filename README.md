# 동훈쌤 홈페이지 — 올리기·설정 안내

## 파일 구성
| 파일 | 역할 |
|---|---|
| `index.html` | 홈 |
| `about/`, `program/`, `center/`, `content/`, `consult/` | 소개, 운동 프로그램, 센터 안내, 콘텐츠, 상담 문의 페이지 |
| `assets/site.css`, `assets/site.js` | 모든 페이지가 같이 쓰는 디자인과 클릭 통계 코드 |
| `images/profile.webp`, `og.jpg` | 프로필 사진, 공유 미리보기 이미지 |
| `robots.txt` | 구글·네이버·AI 검색 로봇에게 수집 허용 |
| `sitemap.xml` | 검색엔진에 제출하는 사이트 지도 |
| `llms.txt` | AI 검색(ChatGPT, Claude, Perplexity 등)이 읽기 쉬운 요약본 |
| `scripts/update_feeds.py` | 유튜브·블로그 최신 글을 콘텐츠 페이지에 넣는 스크립트 |
| `.github/workflows/update-feeds.yml` | 위 스크립트를 매일 오전 6시쯤 자동 실행 |

## 1. 채워 넣을 곳 (index.html)
- 카카오톡 채널을 만들면 상담 영역에 버튼 추가 (요청 시 넣어드림)
- 사진: `images/profile.webp`(홈페이지), `og.jpg`(카톡·SNS 공유 미리보기) 이미 포함

## 블로그 카테고리 바꾸기
`scripts/update_feeds.py` 위쪽의 `BLOG_CATEGORIES` 목록에 있는 카테고리 글만 "PT 후기·운동정보" 페이지에 올라갑니다.
카테고리 이름을 바꾸거나 새로 만들면 이 목록도 똑같이 고쳐주세요. 실행 기록(Actions 탭)에 블로그에서 읽은 카테고리 이름이 찍힙니다.

## 2. 도메인
도메인 `www.healthshindong.com` 이 모든 파일에 이미 들어가 있습니다. `CNAME` 파일은 GitHub Pages가 이 도메인을 쓰도록 알려주는 파일이니 지우지 마세요.

## 3. 올리기 (GitHub Pages, 무료)
1. github.com 가입 → 새 저장소(repository) 만들기, 공개(Public)
2. 이 폴더의 파일을 전부 업로드 (`.github` 폴더 포함)
3. 저장소 Settings → Pages → Branch: `main` / `(root)` → Save
4. 같은 화면 Custom domain에 도메인 입력, 도메인 구매처 DNS에 GitHub 안내대로 레코드 추가, Enforce HTTPS 체크
5. Actions 탭 → "콘텐츠 자동 업데이트" → Run workflow 를 한 번 눌러서 첫 영상·글을 채우기

## 4. 통계 (Google Analytics 4)
1. analytics.google.com → 속성 만들기 → 웹 스트림에 도메인 등록 → 측정 ID(`G-로 시작`) 복사
2. 측정 ID `G-0RNV89RTBC` 가 6개 페이지에 들어가 있음
3. 하루 정도 지나면 관리 → 이벤트 에서 `generate_lead` 를 **주요 이벤트(전환)** 로 표시
4. 관리 → 맞춤 정의 → 맞춤 측정기준 추가: `platform`, `method`, `link_location` (이벤트 범위)

이렇게 하면 보고서에서 볼 수 있는 것:
| 이벤트 | 뜻 | 함께 기록되는 값 |
|---|---|---|
| `click_platform` | 유튜브·블로그·인스타·틱톡으로 나간 클릭 | 어느 채널인지, 페이지 어디서 눌렀는지 |
| `lead_intent` | "상담 문의" 버튼으로 상담 영역까지 내려온 사람 | 눌린 위치 |
| `generate_lead` | 실제 상담 연결 버튼(네이버 예약·전화·DM) 클릭 = 전환 | 상담 수단 |
| `click_map` | 네이버 플레이스·네이버 지도 열기 | 지도 종류 |
유입 경로(네이버 검색, 구글, 인스타 프로필 링크 등)는 GA4가 자동으로 같이 기록합니다.

> 팁: 인스타·유튜브 프로필에 넣는 링크 끝에 `?utm_source=instagram` 처럼 붙이면 어느 SNS에서 몇 명이 왔는지 정확히 구분됩니다.

## 5. 검색 노출 등록
- **구글 서치콘솔** (search.google.com/search-console): 도메인 추가 → HTML 태그 방식의 코드를 홈(`index.html`)의 `google-site-verification` 자리에 넣기 → 확인 → Sitemaps에 `sitemap.xml` 제출
- **네이버 서치어드바이저** (searchadvisor.naver.com): 사이트 등록 → HTML 태그 코드를 홈(`index.html`)의 `naver-site-verification` 자리에 넣기 → 요청 → 사이트맵 제출
- **네이버 플레이스·구글 비즈니스 프로필**: 센터 정보에 홈페이지 주소를 넣어 서로 연결 (지역 검색에 가장 큰 영향)
- 유튜브 채널 정보, 인스타·틱톡 프로필 링크를 이 홈페이지 주소로 통일
