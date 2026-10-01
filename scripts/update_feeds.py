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
    # 채널의 일반 영상(롱폼·미드폼)만 모은 목록: 쇼츠와 라이브는 빠짐
    "https://www.youtube.com/feeds/videos.xml?playlist_id=UULFLtCTZHiue8-5Cg2CtdZDSg",
    # 위 주소가 실패할 때 쓰는 채널 전체 피드 (아래 코드에서 쇼츠를 걸러냄)
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCLtCTZHiue8-5Cg2CtdZDSg",
]
BLOG_RSS = "https://rss.blog.naver.com/hunkyle0104.xml"
MAX_VIDEOS = 15  # 유튜브 피드가 주는 최대 개수
YOUTUBE_FEED_ENABLED = False
MAX_POSTS = 4
BLOG_ID = "hunkyle0104"
THUMB_DIR = ROOT / "images" / "blog"  # 블로그 글 대표 사진을 저장하는 폴더

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
    for e in root.findall("atom:entry", NS):
        vid = e.findtext("yt:videoId", default="", namespaces=NS)
        title = e.findtext("atom:title", default="", namespaces=NS)
        published = e.findtext("atom:published", default="", namespaces=NS)
        link = e.find("atom:link", NS)
        url = link.get("href") if link is not None else f"https://www.youtube.com/watch?v={vid}"
        if "/shorts/" in url or "#shorts" in title.lower():
            continue  # 쇼츠 제외
        items.append({"id": vid, "title": title, "url": url, "date": published[:10]})
        if len(items) >= MAX_VIDEOS:
            break
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
        raw = it.findtext("description") or ""
        desc = re.sub(r"<[^>]+>", " ", raw)
        desc = re.sub(r"\s+", " ", html.unescape(desc)).strip()
        if len(desc) > 80:
            desc = desc[:80].rstrip() + "…"
        m = re.search(r"/(\d{6,})$", url)
        log_no = m.group(1) if m else ""
        img = re.search(r'<img[^>]+src=["\']([^"\']+)', html.unescape(raw))
        items.append({"title": title, "url": url, "date": date, "category": category,
                      "desc": desc, "log_no": log_no, "rss_img": img.group(1) if img else ""})
        if len(items) >= MAX_POSTS:
            break
    # 카테고리 이름이 맞는지 확인할 수 있도록 실행 기록에 남김
    print("블로그 RSS에서 본 카테고리:", ", ".join(sorted(c for c in seen if c)))
    return items


def _post_image_url(post):
    """글의 대표 사진 주소: RSS 안의 사진 → 없으면 글 페이지의 og:image"""
    if post.get("rss_img"):
        return post["rss_img"]
    if not post.get("log_no"):
        return ""
    page = fetch(f"https://m.blog.naver.com/{BLOG_ID}/{post['log_no']}").decode("utf-8", "ignore")
    m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', page) or \
        re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', page)
    return html.unescape(m.group(1)) if m else ""


def _shrink(data, width=720):
    """사진을 가로 720px JPEG로 줄여 페이지가 빨리 뜨게 함 (Pillow가 없으면 원본 그대로)"""
    try:
        from io import BytesIO
        from PIL import Image
        im = Image.open(BytesIO(data)).convert("RGB")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        out = BytesIO()
        im.save(out, "JPEG", quality=78, optimize=True, progressive=True)
        return out.getvalue()
    except Exception as e:
        print("  사진 줄이기 실패, 원본 저장:", e)
        return data


def save_thumbnails(items):
    """대표 사진을 내려받아 images/blog/ 에 저장하고, 지금 쓰지 않는 사진은 지움"""
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    keep = set()
    for p in items:
        p["thumb"] = ""
        name = f"{p['log_no'] or abs(hash(p['url']))}.jpg"
        path = THUMB_DIR / name
        try:
            if not path.exists():
                url = _post_image_url(p)
                if not url:
                    print(f"  사진 없음: {p['title']}")
                    continue
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (homepage feed updater)",
                    "Referer": "https://blog.naver.com/"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = r.read()
                if len(data) < 1000:
                    print(f"  사진이 너무 작음, 건너뜀: {p['title']}")
                    continue
                path.write_bytes(_shrink(data))
            p["thumb"] = f"../images/blog/{name}"
            keep.add(name)
        except Exception as e:
            print(f"  사진 저장 실패 ({p['title']}): {e}")
    for f in THUMB_DIR.glob("*.jpg"):
        if f.name not in keep:
            f.unlink()


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
        if p.get("thumb"):
            pic = f'<span class="pthumb"><img src="{esc(p["thumb"])}" alt="" loading="lazy"></span>'
        else:
            pic = f'<span class="pthumb pthumb-empty"><span>{esc(p["category"])}</span></span>'
        desc = f'<span class="pdesc">{esc(p["desc"])}</span>' if p.get("desc") else ""
        lis.append(
            f'            <li class="post"><a href="{esc(p["url"])}" target="_blank" rel="noopener" '
            f'data-track="platform" data-platform="naver_blog" data-location="content_post">'
            f'{pic}<span class="pbody"><time datetime="{esc(p["date"])}">{esc(p["date"])} · {esc(p["category"])}</time>'
            f'<b>{esc(p["title"])}</b>{desc}</span></a></li>'
        )
    return '          <ul class="posts">\n' + "\n".join(lis) + "\n          </ul>"


def replace_block(text, name, inner):
    pattern = re.compile(rf"(<!-- FEED:{name}:START -->\n).*?(\n<!-- FEED:{name}:END -->)", re.S)
    if not pattern.search(text):
        sys.exit(f"content/index.html에서 FEED:{name} 표시를 찾지 못했습니다.")
    return pattern.sub(lambda m: m.group(1) + inner + m.group(2), text)


def main():
    text = INDEX.read_text(encoding="utf-8")
    original = text
    # 유튜브는 콘텐츠 페이지에 '롱폼 전체 재생목록'을 직접 넣어 두어서 자동으로 최신 상태가 유지됩니다.
    # (유튜브 RSS가 GitHub 서버에서 막혀 있어 피드 방식은 끔. 필요하면 True로 바꾸세요)
    try:
        if not YOUTUBE_FEED_ENABLED:
            raise RuntimeError("유튜브 피드 사용 안 함 (재생목록 임베드 사용 중)")
        yt = youtube_items()
        if yt:
            text = replace_block(text, "YOUTUBE", render_youtube(yt))
        print(f"유튜브 {len(yt)}개")
    except Exception as e:
        print("유튜브 피드를 읽지 못했습니다. 기존 목록을 유지합니다:", e)
    try:
        bl = blog_items()
        save_thumbnails(bl)
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
