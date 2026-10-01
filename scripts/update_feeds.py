"""
유튜브 채널과 네이버 블로그의 RSS를 읽어서 content/index.html(콘텐츠 페이지)을 최신 글로 바꿔 넣는 스크립트.
GitHub Actions가 매일 실행합니다(.github/workflows/update-feeds.yml). 외부 패키지 없이 파이썬 기본 기능만 씁니다.
검색엔진이 읽을 수 있도록 HTML 안에 직접 글 목록을 써 넣습니다.
"""
import html
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "content" / "index.html"
SITEMAP = ROOT / "sitemap.xml"

YOUTUBE_RSS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCLtCTZHiue8-5Cg2CtdZDSg",
    # 같은 채널의 '업로드 영상' 목록 (위 주소가 가끔 404를 줄 때 대신 사용)
    "https://www.youtube.com/feeds/videos.xml?playlist_id=UULtCTZHiue8-5Cg2CtdZDSg",
]
BLOG_RSS = "https://rss.blog.naver.com/hunkyle0104.xml"
MAX_VIDEOS = 6
MAX_POSTS = 6

# 'PT 후기·운동정보' 페이지에 올릴 블로그 카테고리 ('원앤온리PT 동훈쌤' 아래 하위 카테고리 이름과 똑같이 적기)
# 비워두면 ([]) 모든 글을 올립니다.
BLOG_CATEGORIES = [
    "동훈쌤 소개",
    "PT 후기",
    "원앤온리PT",
    "비골 골절 비수술",
    "건강/운동 정보",
]

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (homepage feed updater)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def fetch_any(urls, tries=3):
    """여러 주소를 번갈아 몇 번 시도해서 처음 성공한 응답을 돌려줌"""
    last = None
    for attempt in range(tries):
        for url in urls:
            try:
                return fetch(url)
            except Exception as e:
                last = e
                print(f"  {url} 실패 ({e})")
        time.sleep(5 * (attempt + 1))
    raise last


def youtube_items():
    root = ET.fromstring(fetch_any(YOUTUBE_RSS))
    items = []
    for e in root.findall("atom:entry", NS)[:MAX_VIDEOS]:
        vid = e.findtext("yt:videoId", default="", namespaces=NS)
        title = e.findtext("atom:title", default="", namespaces=NS)
        published = e.findtext("atom:published", default="", namespaces=NS)
        link = e.find("atom:link", NS)
        url = link.get("href") if link is not None else f"https://www.youtube.com/watch?v={vid}"
        items.append({"id": vid, "title": title, "url": url, "date": published[:10]})
    return items


def _norm(s):
    return re.sub(r"\s+", "", s or "")


def blog_items():
    root = ET.fromstring(fetch(BLOG_RSS))
    allowed = {_norm(c) for c in BLOG_CATEGORIES}
    items, seen = [], set()
    for it in root.findall("./channel/item"):
        category = (it.findtext("category") or "").strip()
        seen.add(category)
        if allowed and _norm(category) not in allowed:
            continue
        title = (it.findtext("title") or "").strip()
        url = (it.findtext("link") or "").strip().split("?")[0]
        try:
            date = parsedate_to_datetime(it.findtext("pubDate")).strftime("%Y-%m-%d")
        except Exception:
            date = ""
        items.append({"title": title, "url": url, "date": date, "category": category})
        if len(items) >= MAX_POSTS:
            break
    # 카테고리 이름이 맞는지 확인할 수 있도록 실행 기록에 남김
    print("블로그 RSS에서 본 카테고리:", ", ".join(sorted(c for c in seen if c)))
    return items


def esc(s):
    return html.escape(s, quote=True)


def render_youtube(items):
    lis = []
    for v in items:
        lis.append(
            f'            <li class="card"><a href="{esc(v["url"])}" target="_blank" rel="noopener" '
            f'data-track="platform" data-platform="youtube" data-location="content_video">'
            f'<span class="thumb"><img src="https://i.ytimg.com/vi/{esc(v["id"])}/hqdefault.jpg" '
            f'alt="{esc(v["title"])}" loading="lazy" width="480" height="360"></span>'
            f'<b>{esc(v["title"])}</b><time datetime="{esc(v["date"])}">{esc(v["date"])}</time></a></li>'
        )
    return '          <ul class="cards">\n' + "\n".join(lis) + "\n          </ul>"


def render_blog(items):
    lis = []
    for p in items:
        lis.append(
            f'            <li class="post"><a href="{esc(p["url"])}" target="_blank" rel="noopener" '
            f'data-track="platform" data-platform="naver_blog" data-location="content_post">'
            f'<time datetime="{esc(p["date"])}">{esc(p["date"])} · {esc(p["category"])}</time><b>{esc(p["title"])}</b></a></li>'
        )
    return '          <ul class="cards">\n' + "\n".join(lis) + "\n          </ul>"


def replace_block(text, name, inner):
    pattern = re.compile(rf"(<!-- FEED:{name}:START -->\n).*?(\n<!-- FEED:{name}:END -->)", re.S)
    if not pattern.search(text):
        sys.exit(f"content/index.html에서 FEED:{name} 표시를 찾지 못했습니다.")
    return pattern.sub(lambda m: m.group(1) + inner + m.group(2), text)


def main():
    text = INDEX.read_text(encoding="utf-8")
    original = text
    try:
        yt = youtube_items()
        if yt:
            text = replace_block(text, "YOUTUBE", render_youtube(yt))
        print(f"유튜브 {len(yt)}개")
    except Exception as e:
        print("유튜브 피드를 읽지 못했습니다. 기존 목록을 유지합니다:", e)
    try:
        bl = blog_items()
        if bl:
            text = replace_block(text, "BLOG", render_blog(bl))
        print(f"블로그 {len(bl)}개")
    except Exception as e:
        print("블로그 피드를 읽지 못했습니다. 기존 목록을 유지합니다:", e)

    if text != original:
        INDEX.write_text(text, encoding="utf-8")
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        sm = SITEMAP.read_text(encoding="utf-8")
        SITEMAP.write_text(re.sub(r"<lastmod>.*?</lastmod>", f"<lastmod>{today}</lastmod>", sm), encoding="utf-8")
        print("콘텐츠 페이지 갱신 완료")
    else:
        print("새 콘텐츠 없음")


if __name__ == "__main__":
    main()
