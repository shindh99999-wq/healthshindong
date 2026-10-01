"""6페이지 사이트 생성기.
페이지 문구를 고칠 때는 이 파일(또는 onepage.html)을 고친 뒤 `python3 _src/build.py site` 로 6개 페이지를 다시 만듭니다.
주의: content/index.html 의 FEED 영역은 매일 자동 업데이트가 채우므로, 다시 만든 뒤 Actions에서 업데이트를 한 번 실행하세요.
"""
import json, re, sys, shutil
from pathlib import Path

HERE = Path(__file__).parent
ONE = (HERE / "onepage.html").read_text(encoding="utf-8")
MODE = sys.argv[1] if len(sys.argv) > 1 else "site"
SITE = HERE.parent  # 저장소 루트 (_src 의 상위 폴더)
OUT = SITE if MODE == "site" else Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/preview")
DOMAIN = "https://www.healthshindong.com"

def grab(pattern, flags=re.S):
    m = re.search(pattern, ONE, flags)
    assert m, pattern
    return m.group(1)

CSS = grab(r"<style>\n(.*?)</style>")
JS = grab(r"<script>\n(\(function \(\) \{.*?)</script>")
GA = grab(r"(<!-- Google Analytics 4.*?</script>)")
GRAPH = json.loads(grab(r'<script type="application/ld\+json">(.*?)</script>'))
FONTS = grab(r'(<link rel="preconnect" href="https://fonts.googleapis.com">.*?display=swap">)')
ICON = grab(r'(<link rel="icon"[^>]+>)')

def section(id_):
    return grab(rf'(<section class="block" id="{id_}">.*?\n  </section>)')

HERO = grab(r'(<section class="hero">.*?\n  </section>)')
ABOUT = section("about")
PROGRAM = section("program")
CENTER = section("center")
CONTENT = section("content")
SOCIAL = grab(r'(        <div>\n          <div class="feed-head"><h3>짧은 영상은 여기서</h3></div>.*?\n          </div>\n        </div>)')
FAQ = section("faq")
CONSULT = section("consult")

YT = "https://www.youtube.com/@%EA%B1%B4%EA%B0%95%EC%8B%A0%EB%8F%99%EB%8F%99%ED%9B%88%EC%8C%A4"
BOOK = "https://naver.me/Gq8oYAK2"
CUR = ' aria-current="page"'

PAGES = [
    # key, path(site), file(preview), nav label, title, description, eyebrow
    ("home", "", "index.html", "홈", "부산교대 재활PT · 동훈쌤 신동훈",
     "부산 연제구 재활PT, 원앤온리PT 부산교대점 동훈쌤(신동훈). 만성 통증, 수술 후 재활, 무릎·허리 통증, 고혈압·당뇨·고지혈증 운동, 시니어 운동까지 1:1로 평가하고 운동으로 돕습니다. 네이버 예약, 전화 0507-1471-0290."),
    ("about", "about/", "about.html", "소개", "소개 · 재활PT 동훈쌤 신동훈",
     "부산교대 재활PT 트레이너 신동훈(동훈쌤) 소개. 아픈 부위만이 아니라 움직임 전체와 생활까지 함께 보는 생물심리사회적 관점으로 재활 운동을 지도합니다."),
    ("program", "program/", "program.html", "운동 프로그램", "운동 프로그램 · 부산교대 재활PT 동훈쌤",
     "만성 통증, 수술 후 재활, 무릎 통증, 허리 통증, 대사성 질환(고혈압·당뇨·고지혈증), 시니어 운동. MAT·Motor Control·DNS·STC·기능성 운동·근력 운동으로 진행하는 부산 재활PT 프로그램."),
    ("center", "center/", "center.html", "센터 안내", "센터 안내 · 원앤온리PT 부산교대점",
     "원앤온리PT 부산교대점 위치와 운영 시간. 부산광역시 연제구 명륜로 2번길 7, 삼익퓨처타워상가 306호. 평일 10시~22시, 토요일 10시~14시, 일·공휴일 휴무. 전화 0507-1471-0290."),
    ("content", "content/", "content.html", "PT 후기·운동정보", "PT 후기·운동정보 · 부산교대 재활PT 동훈쌤",
     "부산교대 재활PT 동훈쌤의 실제 PT 후기와 회원 사례, 유튜브 건강신동 동훈쌤 영상과 건강·운동 정보 글을 모아 봅니다."),
    ("consult", "consult/", "consult.html", "상담 문의", "상담 문의 · 부산교대 재활PT 동훈쌤",
     "부산교대 재활PT 상담 문의. 네이버 예약, 전화 0507-1471-0290, 인스타그램 DM으로 문의하세요. 통증·수술 후 재활·대사성 질환 운동에 관해 자주 묻는 질문도 확인할 수 있습니다."),
]
P = {p[0]: p for p in PAGES}

def href(cur, target, anchor=""):
    if MODE == "preview":
        return P[target][2] + anchor
    up = "" if cur == "home" else "../"
    path = P[target][1]
    return (up + path if (up + path) else "./") + anchor

def abs_url(key):
    return f"{DOMAIN}/{P[key][1]}"

# ---------------- 재활 분야 ----------------
FOCUS = [
    ("chronic", "만성 통증", "3개월 넘게 이어지거나 좋아졌다 나빠지기를 반복하는 통증. 몸 상태와 함께 수면, 스트레스, 움직임에 대한 걱정까지 살피며 다시 움직일 자신감을 되찾습니다."),
    ("surgery", "수술 후 재활", "십자인대·반월판, 어깨, 허리 수술 이후 병원 재활을 마친 다음 단계. 담당 의료진의 지침 범위 안에서 일상과 운동 복귀까지 단계적으로 진행합니다."),
    ("knee", "무릎 통증", "계단, 쪼그려 앉기, 달리기에서 아픈 무릎. 무릎만 보지 않고 고관절과 발목이 무릎에 주는 부담까지 함께 찾아 조정합니다."),
    ("back", "허리 통증", "디스크 진단 이후나 자주 반복되는 허리 통증. 호흡과 몸통 안정성을 다시 세우고, 굽히고 들어 올리는 동작을 안전하게 다시 익힙니다."),
    ("metabolic", "대사성 질환", "고혈압, 당뇨, 고지혈증이 있어도 운동은 관리의 기본입니다. 혈압과 혈당 상태, 복용 중인 약을 확인하고 자신에게 필요한 유산소 운동과 근력 운동을 단계별로 진행합니다."),
    ("senior", "시니어 운동", "나이가 들면서 줄어드는 근력과 균형을 지키는 운동. 낙상을 예방하고 계단 오르기, 의자에서 일어나기 같은 동작을 연습해서, 관절이 아픈 분들도 산책, 장보기, 외출 같은 일상생활을 다시 편하게 할 수 있도록 1:1로 돕습니다."),
]

def focus_detail():
    items = "\n".join(
        f'        <article id="{k}">\n          <h3>{t}</h3>\n          <p>{d}</p>\n        </article>' for k, t, d in FOCUS)
    return f'      <div class="focus" id="focus">\n{items}\n      </div>'

def focus_summary(cur):
    items = "\n".join(
        f'        <a class="fcard" href="{href(cur, "program", "#" + k)}"><b>{t}</b><span>{d.split(". ")[0].rstrip(".")}.</span></a>'
        for k, t, d in FOCUS)
    return f'      <div class="fgrid">\n{items}\n      </div>'

def tags(cur):
    return "\n".join(f'          <li><a href="{href(cur, "program", "#" + k)}">{t}</a></li>' for k, t, _ in FOCUS)

# ---------------- 공통 조각 ----------------
def header(cur):
    links = "\n".join(
        f'      <a href="{href(cur, k)}"{CUR if k == cur else ""}>{P[k][3]}</a>'
        for k in ["about", "program", "center", "content", "consult"])
    return f'''<header class="top">
  <div class="wrap">
    <a class="brand" href="{href(cur, "home")}"><b>동훈쌤</b><span>재활PT 신동훈</span></a>
    <nav class="nav" aria-label="주요 메뉴">
{links}
    </nav>
    <a class="btn btn-cta" href="{BOOK}" target="_blank" rel="noopener" data-track="lead" data-method="naver_booking" data-location="header">네이버 예약</a>
  </div>
</header>'''

def footer(cur):
    links = " · ".join(f'<a href="{href(cur, k)}">{P[k][3]}</a>' for k in ["home", "about", "program", "center", "content", "consult"])
    return f'''<footer>
  <div class="wrap">
    <p class="flinks">{links}</p>
    <p>원앤온리PT 부산교대점 · 부산광역시 연제구 명륜로 2번길 7, 삼익퓨처타워상가 306호 · 전화 0507-1471-0290</p>
    <p>이 사이트의 정보는 일반적인 운동 안내이며 의학적 진단을 대신하지 않습니다.</p>
  </div>
</footer>

<div class="dock">
  <a class="btn btn-ghost" href="tel:050714710290" data-track="lead" data-method="phone" data-location="mobile_dock">전화 상담</a>
  <a class="btn btn-cta" href="{BOOK}" target="_blank" rel="noopener" data-track="lead" data-method="naver_booking" data-location="mobile_dock">네이버 예약</a>
</div>'''

def band(cur):
    return f'''  <section class="block">
    <div class="wrap">
      <div class="band">
        <div>
          <h2>어디가, 언제부터 불편한지<br>편하게 말씀해 주세요</h2>
          <p class="lead">첫 시간은 상담과 움직임 평가부터 진행합니다.</p>
        </div>
        <div class="band-actions">
          <a class="btn btn-cta" href="{BOOK}" target="_blank" rel="noopener" data-track="lead" data-method="naver_booking" data-location="band">네이버로 예약하기</a>
          <a class="btn btn-line" href="tel:050714710290" data-track="lead" data-method="phone" data-location="band">전화 0507-1471-0290</a>
          <a class="btn btn-line" href="{href(cur, "consult")}" data-track="lead_intent" data-location="band">다른 상담 방법 보기</a>
        </div>
      </div>
    </div>
  </section>'''

def page_head(eyebrow, h1, lead=""):
    lead_html = f'\n      <p class="lead">{lead}</p>' if lead else ""
    return f'''  <section class="page-head">
    <div class="wrap">
      <p class="eyebrow">{eyebrow}</p>
      <h1>{h1}</h1>{lead_html}
    </div>
  </section>'''

def strip_head(sec):
    """섹션의 eyebrow+h2 머리를 없애고 본문만 남김 (페이지 머리가 대신함)"""
    return re.sub(r'\n      <div class="head">\n        <p class="eyebrow">[^<]*</p>\n        <h2>[^<]*</h2>\n      </div>', "", sec, count=1)

def rel_links(sec, cur):
    sec = sec.replace('href="#consult"', f'href="{href(cur, "consult")}"')
    sec = sec.replace('href="#program"', f'href="{href(cur, "program")}"')
    return sec

# ---------------- 페이지 본문 ----------------
STEPS = grab(r'(      <ol class="steps".*?</ol>)').replace("일상과 운동에서 버틸 힘으로 만들기</span>", "일상과 운동에서 버틸 힘으로 만들기. 통증이 줄어든 뒤에는 체력과 몸 만들기까지 이어갑니다</span>")
PROGS = grab(r'(      <div class="programs">.*?\n      </div>\n)')
FAQ_NEW_Q = "고혈압, 당뇨, 고지혈증이 있어도 운동해도 되나요?"
FAQ_NEW_A = "대부분은 규칙적인 유산소 운동과 근력 운동이 관리에 도움이 되어 권장됩니다. 다만 혈압이나 혈당 조절이 불안정하거나 최근 약을 바꿨다면 먼저 담당 의사와 상의해 주세요. 수업에서는 그날의 컨디션과 복용 중인 약을 확인하고 운동 강도를 조절합니다."
FAQ_PRICE_Q = "재활PT 비용은 얼마인가요?"
FAQ_PRICE_A = "1:1 수업 기준 1회 10만 원, 10회 80만 원, 20회 150만 원, 30회 210만 원, 50회 350만 원입니다. 재활, 수술 후 운동재활, 맞춤 운동 모두 같은 비용이며, 필요한 횟수는 첫 상담과 평가 후 함께 정합니다."
FAQ_DIET_Q = "다이어트나 몸 만들기도 할 수 있나요?"
FAQ_DIET_A = "가능합니다. 무리한 식단이나 고강도 운동부터 시작하지 않고, 관절에 부담이 덜한 움직임을 먼저 익힌 뒤 근력 운동을 늘려가며 체지방을 관리합니다. 통증이나 수술 이력이 있는 분도 같은 방식으로 진행합니다."


CREDS = [("학력", "동아대학교 체육학과 졸업"), ("학력", "부산외국어대학교 스포츠재활 석사 졸업"),
         ("강의", "KESRA 한국운동과학연구협회 MASTER 강사"),
         ("자격", "생활스포츠지도사 2급 (보디빌딩)"), ("자격", "Muscle Activation Technique (MAT)"),
         ("자격", "Movement Science Specialist (MSS)")]
PRICES = [(1, 10), (10, 80), (20, 150), (30, 210), (50, 350)]

def _cred_price():
    rows = "\n".join(f'          <div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in CREDS)
    trs = "\n".join(
        f'            <tr><th scope="row">{n}회</th><td>{t}만 원</td><td>{t/n:g}만 원</td></tr>'
        for n, t in PRICES)
    return f'''  <section class="block">
    <div class="wrap">
      <div class="cp">
        <div>
          <div class="head">
            <p class="eyebrow">경력·자격</p>
            <h2>원앤온리PT 부산교대점 대표 신동훈</h2>
          </div>
          <dl class="creds">
{rows}
          </dl>
        </div>
        <div>
          <div class="head">
            <p class="eyebrow">비용</p>
            <h2>1:1 재활PT 비용</h2>
          </div>
          <div class="price-wrap">
          <table class="price">
            <thead><tr><th scope="col">횟수</th><th scope="col">금액</th><th scope="col">회당</th></tr></thead>
            <tbody>
{trs}
            </tbody>
          </table>
          </div>
          <p class="price-note">만성 근골격계 질환 재활, 수술 후 운동재활, 일반 운동 재활, 기능 회복 운동, 맞춤 운동 모두 같은 비용입니다. 몇 회가 필요한지는 첫 상담과 평가 후에 함께 정합니다.</p>
        </div>
      </div>
    </div>
  </section>'''

CRED_PRICE = _cred_price()

def body(cur):
    if cur == "home":
        hero = HERO
        hero = re.sub(r'(<ul class="focus-tags" aria-label="재활 분야">\n).*?(\n        </ul>)', lambda m: m.group(1) + tags(cur) + m.group(2), hero, flags=re.S)
        hero = rel_links(hero, cur)
        hero = hero.replace("<strong>재활PT 트레이너 신동훈(동훈쌤)</strong>입니다.", "<strong>원앤온리PT 부산교대점 대표, 재활PT 트레이너 신동훈(동훈쌤)</strong>입니다.")
        hero = hero.replace("<span>재활PT 트레이너 · 동훈쌤</span>", "<span>대표 · 재활PT 트레이너</span>")
        hero = hero.replace(f'href="{href(cur, "consult")}" data-track="lead_intent" data-location="hero">상담 문의하기',
                            f'href="{BOOK}" target="_blank" rel="noopener" data-track="lead" data-method="naver_booking" data-location="hero">네이버로 예약하기')
        return f'''{hero}

  <section class="block">
    <div class="wrap">
      <div class="head">
        <p class="eyebrow">재활 분야</p>
        <h2>이런 분들의 재활과 운동을 돕습니다</h2>
      </div>
{focus_summary(cur)}
    </div>
  </section>

  <section class="block">
    <div class="wrap">
      <div class="head">
        <p class="eyebrow">진행 방식</p>
        <h2>평가부터 시작해서, 내 몸에 맞는 운동까지</h2>
      </div>
{STEPS}
      <p class="next"><a class="more" href="{href(cur, "program")}">운동 프로그램 자세히 보기 →</a></p>
    </div>
  </section>

{band(cur)}'''

    if cur == "about":
        sec = strip_head(ABOUT).replace('<section class="block" id="about">', '<section class="block first">')
        return page_head("소개", "통증 부위보다, 그 부위가 일을 떠안게 된 이유를 찾습니다") + "\n\n" + sec + "\n\n" + CRED_PRICE + "\n\n" + band(cur)

    if cur == "program":
        return page_head("운동 프로그램", "이런 분들의 재활과 운동을 돕습니다",
                         "통증 재활부터 대사성 질환 운동, 시니어 운동까지 1:1로 평가하고 진행합니다.") + f'''

  <section class="block first">
    <div class="wrap">
{focus_detail()}
    </div>
  </section>

  <section class="block">
    <div class="wrap">
      <div class="head">
        <p class="eyebrow">운동 방법</p>
        <h2>네 가지 방법을 몸 상태에 맞게 조합합니다</h2>
        <p class="lead">한 가지 기법만 고집하지 않습니다. 평가 결과에 따라 필요한 방법을 골라 순서대로 적용합니다.</p>
      </div>
{PROGS}    </div>
  </section>

  <section class="block">
    <div class="wrap">
      <div class="head">
        <p class="eyebrow">진행 순서</p>
        <h2>평가 → 원인 → 내 몸에 맞는 움직임 → 운동</h2>
      </div>
{STEPS}
    </div>
  </section>

{band(cur)}'''

    if cur == "center":
        sec = strip_head(CENTER).replace('<section class="block" id="center">', '<section class="block first">')
        return page_head("센터 안내", "원앤온리PT 부산교대점", "부산광역시 연제구 명륜로 2번길 7, 삼익퓨처타워상가 306호") + "\n\n" + sec + "\n\n" + band(cur)

    if cur == "content":
        sec = strip_head(CONTENT).replace('<section class="block" id="content">', '<section class="block first">')
        return page_head("PT 후기·운동정보", "새 영상과 글이 올라오면 여기에도 자동으로 올라옵니다",
                         "유튜브 건강신동 동훈쌤과 네이버 블로그의 최신 후기·운동 정보입니다.") + "\n\n" + sec + "\n\n" + band(cur)

    if cur == "consult":
        cons = CONSULT.replace('<section class="block" id="consult">', '<section class="block first">')
        cons = cons.replace('<p class="eyebrow" style="color: var(--amber);">상담 문의</p>\n          <h2>', '<p class="eyebrow" style="color: var(--amber);">상담 문의</p>\n          <h1 class="ch1">')
        cons = cons.replace('편하게 말씀해 주세요</h2>', '편하게 말씀해 주세요</h1>')
        faq = FAQ.replace('<section class="block" id="faq">', '<section class="block" id="faq">')
        extra = (f'\n        <div><dt>{FAQ_PRICE_Q}</dt><dd>{FAQ_PRICE_A}</dd></div>'
                 f'\n        <div><dt>{FAQ_NEW_Q}</dt><dd>{FAQ_NEW_A}</dd></div>'
                 f'\n        <div><dt>{FAQ_DIET_Q}</dt><dd>{FAQ_DIET_A}</dd></div>')
        faq = faq.replace('\n      </dl>', extra + '\n      </dl>')
        return cons + "\n\n" + faq

def jsonld(cur):
    graph = [g for g in GRAPH["@graph"] if g["@type"] != "FAQPage"]
    for g in graph:
        if g["@type"] == "Person":
            g["knowsAbout"] = [k for k in g["knowsAbout"]] + ["고혈압 운동", "당뇨 운동", "고지혈증 운동", "시니어 운동", "낙상 예방 운동"]
            g["jobTitle"] = "원앤온리PT 부산교대점 대표 · 재활PT 트레이너"
            g["alumniOf"] = [{"@type": "CollegeOrUniversity", "name": "동아대학교"}, {"@type": "CollegeOrUniversity", "name": "부산외국어대학교"}]
            g["hasCredential"] = [{"@type": "EducationalOccupationalCredential", "name": n} for n in ["생활스포츠지도사 2급 (보디빌딩)", "Muscle Activation Technique (MAT)", "Movement Science Specialist (MSS)"]]
            g["description"] = "부산 원앤온리PT 부산교대점에서 만성 통증, 수술 후 재활, 무릎·허리 통증, 대사성 질환 운동, 시니어 운동을 MAT, Motor Control, DNS, STC, 기능성 운동, 근력 운동으로 지도하는 재활PT 트레이너."
    for g in graph:
        if "ExerciseGym" in g["@type"]:
            g["priceRange"] = "1회 10만 원, 10회 80만 원, 20회 150만 원, 30회 210만 원, 50회 350만 원"
    out = {"@context": "https://schema.org", "@graph": graph}
    if cur != "home":
        out["@graph"] = out["@graph"] + [{
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "홈", "item": abs_url("home")},
                {"@type": "ListItem", "position": 2, "name": P[cur][3], "item": abs_url(cur)}]}]
    if cur == "consult":
        faq = next(g for g in GRAPH["@graph"] if g["@type"] == "FAQPage")
        faq = json.loads(json.dumps(faq))
        for q, a in [(FAQ_PRICE_Q, FAQ_PRICE_A), (FAQ_NEW_Q, FAQ_NEW_A), (FAQ_DIET_Q, FAQ_DIET_A)]:
            faq["mainEntity"].append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
        out["@graph"].append(faq)
    return json.dumps(out, ensure_ascii=False, indent=1)

EXTRA_CSS = """
/* ---------- multi-page additions ---------- */
.nav a[aria-current="page"] { color: var(--ink); font-weight: 700; }
.navrow { display: flex; gap: 6px; overflow-x: auto; padding: 0 20px 10px; scrollbar-width: none; }
.navrow::-webkit-scrollbar { display: none; }
.navrow a { flex: none; padding: 6px 12px; border-radius: 999px; font-size: 14px; text-decoration: none; color: var(--muted); background: var(--surface); border: 1px solid var(--line); }
.navrow a[aria-current="page"] { background: var(--ink); color: var(--bg); border-color: var(--ink); }
@media (min-width: 860px) { .navrow { display: none; } }
.page-head { padding-block: 56px 8px; }
.page-head h1 { font-family: var(--display); font-weight: 400; font-size: clamp(32px, 5.4vw, 52px); line-height: 1.2; letter-spacing: -.01em; max-width: 22ch; }
.page-head .lead { margin-top: 14px; font-size: 17px; }
section.block.first { border-top: 0; padding-top: 40px; }
.consult .ch1 { font-family: var(--display); font-weight: 400; font-size: clamp(28px, 4.2vw, 40px); line-height: 1.25; color: var(--bg); }
.fgrid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr)); }
.fcard { display: grid; gap: 6px; align-content: start; padding: 20px; border-radius: var(--radius); background: var(--surface); border: 1px solid var(--line); text-decoration: none; transition: border-color .15s ease; }
.fcard:hover { border-color: var(--pine); }
.fcard b { font-size: 18px; color: var(--pine); }
.fcard span { color: var(--muted); font-size: 14.5px; line-height: 1.6; }
.next { margin-top: 24px; }
.band { display: grid; gap: 24px; padding: clamp(24px, 4vw, 40px); border-radius: 20px; background: var(--pine-soft); }
@media (min-width: 860px) { .band { grid-template-columns: 1fr auto; align-items: center; } }
.band h2 { font-size: clamp(24px, 3.4vw, 32px); }
.band .lead { margin-top: 10px; }
.band-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.btn-line { background: var(--surface); color: var(--ink); border: 1.5px solid var(--line); }
.flinks a { text-decoration: none; color: var(--ink); }
.flinks a:hover { color: var(--pine); }
.focus article { scroll-margin-top: 80px; }
.yt-embed { aspect-ratio: 16 / 9; max-width: 100%; border-radius: 14px; overflow: hidden; background: var(--pine-soft); }
.yt-embed iframe { width: 100%; height: 100%; border: 0; display: block; }
.yt-note { margin-top: 10px; color: var(--muted); font-size: 14px; }
.posts { list-style: none; padding: 0; margin: 0; display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(min(100%, 260px), 1fr)); }
.post a { display: grid; grid-template-rows: auto 1fr; height: 100%; border: 1px solid var(--line); border-radius: 14px; overflow: hidden; background: var(--surface); text-decoration: none; transition: border-color .15s ease; }
.post a:hover { border-color: var(--pine); }
.post a:hover b { color: var(--pine); }
.pthumb { display: block; aspect-ratio: 16 / 10; max-width: 100%; background: var(--pine-soft); overflow: hidden; }
.pthumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.pthumb-empty { display: grid; place-items: center; color: var(--pine); font-weight: 700; font-size: 15px; }
.pbody { display: grid; gap: 6px; align-content: start; padding: 16px 18px 18px; min-width: 0; }
.pbody time { font-family: var(--mono); font-size: 12.5px; color: var(--muted); }
.pbody b { font-size: 16px; line-height: 1.45; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.pdesc { color: var(--muted); font-size: 14px; line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
h2.sub { font-size: clamp(24px, 3.4vw, 30px); }
#reviews .feed-head, #info > .wrap > .feed-head { margin-bottom: 24px; }
.cp { display: grid; gap: 48px; }
@media (min-width: 900px) { .cp { grid-template-columns: 1fr 1fr; gap: 56px; } }
.cp .head { margin-bottom: 24px; }
.creds { margin: 0; display: grid; border-top: 2px solid var(--ink); }
.creds div { display: grid; grid-template-columns: 56px 1fr; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--line); }
.creds dt { font-family: var(--mono); font-size: 12.5px; color: var(--pine); padding-top: 3px; }
.creds dd { margin: 0; font-weight: 500; }
.price-wrap { overflow-x: auto; }
.price { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
.price th, .price td { text-align: left; padding: 14px 8px; border-bottom: 1px solid var(--line); }
.price thead th { font-family: var(--mono); font-size: 12.5px; font-weight: 500; color: var(--muted); border-bottom: 2px solid var(--ink); }
.price tbody th { font-weight: 700; }
.price td:nth-child(2) { font-family: var(--display); font-weight: 400; font-size: 22px; }
.price td:nth-child(3) { color: var(--muted); }
.price-note { margin-top: 16px; color: var(--muted); font-size: 14.5px; }
"""

def head(cur, prev_main=False):
    key, path, file, label, title, desc = P[cur]
    if MODE == "preview":
        css = f"<style>\n{CSS}{EXTRA_CSS}</style>"
        meta = f"<title>{'동훈쌤 홈페이지' if cur == 'home' else title}</title>\n{FONTS}\n{css}"
        return meta
    url = abs_url(cur)
    return f'''<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow">
<meta name="google-site-verification" content="GOOGLE_VERIFICATION_CODE">
<meta name="naver-site-verification" content="NAVER_VERIFICATION_CODE">
<meta property="og:type" content="website">
<meta property="og:locale" content="ko_KR">
<meta property="og:site_name" content="동훈쌤 신동훈">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/og.jpg">
<meta name="twitter:card" content="summary_large_image">
{ICON}
{FONTS}
<link rel="stylesheet" href="{'' if cur == 'home' else '../'}assets/site.css">
<script type="application/ld+json">
{jsonld(cur)}
</script>
{GA}'''

def navrow(cur):
    return '<nav class="navrow" aria-label="페이지 메뉴">' + "".join(
        f'<a href="{href(cur, k)}"{CUR if k == cur else ""}>{P[k][3]}</a>' for k in ["home", "about", "program", "center", "content", "consult"]) + "</nav>"

def render(cur):
    hdr = header(cur).replace("  </div>\n</header>", "  </div>\n  " + navrow(cur) + "\n</header>")
    img = "images/profile.webp" if (MODE == "preview" or cur == "home") else "../images/profile.webp"
    main = body(cur).replace('src="images/profile.webp"', f'src="{img}"')
    script = (f"<script>\n{JS}</script>" if MODE == "preview"
              else f'<script src="{"" if cur == "home" else "../"}assets/site.js" defer></script>')
    inner = f"{hdr}\n\n<main>\n{main}\n</main>\n\n{footer(cur)}\n\n{script}\n"
    if MODE == "preview" and cur == "home":
        return head(cur) + "\n" + inner
    return f'<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head(cur)}\n</head>\n<body>\n{inner}</body>\n</html>\n'

def main():
    if MODE == "preview":
        shutil.rmtree(OUT, ignore_errors=True)
        (OUT / "images").mkdir(parents=True)
        shutil.copy(SITE / "images/profile.webp", OUT / "images/profile.webp")
    else:
        (OUT / "assets").mkdir(exist_ok=True)
        (OUT / "assets/site.css").write_text(CSS + EXTRA_CSS, encoding="utf-8")
        (OUT / "assets/site.js").write_text(JS, encoding="utf-8")
    for key, path, file, *_ in PAGES:
        target = OUT / file if MODE == "preview" else OUT / path / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(key), encoding="utf-8")
        print("wrote", target)

main()
