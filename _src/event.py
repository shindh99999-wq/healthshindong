"""11월 원앤온리PT 5주년 이벤트 (2026-11-30까지).

기간이 지나면
- 방문자 화면: 12월 1일 0시(한국 시간)에 바로 숨겨짐 (페이지 안 작은 스크립트)
- 페이지 파일: 매일 아침 자동 업데이트가 scripts/remove_expired_event.py 로 지움
- build.py 로 다시 만들 때도 기간이 지났으면 넣지 않음
"""
from datetime import datetime, timezone, timedelta

EVENT_END_ISO = "2026-12-01T00:00:00+09:00"   # 이 시각부터 사라짐 (= 11월 30일까지)
EVENT_ON = datetime.now(timezone(timedelta(hours=9))) < datetime.fromisoformat(EVENT_END_ISO)
# (횟수, 정상가 만 원, 이벤트가 만 원)
EVENT_PRICES = [(10, 80, 70), (20, 150, 130), (30, 210, 180), (40, 280, 240), (50, 350, 300), (60, 420, 360)]
EVENT_MAX_OFF = max(n - e for _, n, e in EVENT_PRICES)

EVENT_HIDE = (
    "<script>(function(){var end=Date.parse('" + EVENT_END_ISO + "');"
    "if(Date.now()>=end){document.querySelectorAll('.js-event').forEach(function(e){e.remove();});return;}"
    "var d=document.getElementById('evDday');if(d){var n=Math.ceil((end-Date.now())/864e5);"
    "d.textContent=n<=1?'오늘 마감':'마감까지 D-'+(n-1);d.hidden=false;}})();</script>"
)


def event_section(book):
    if not EVENT_ON:
        return ""
    rows = "\n".join(
        f'            <tr><th scope="row">{c}회</th><td class="ev-was"><s>{n}만 원</s></td>'
        f'<td class="ev-now">{e}만 원</td><td class="ev-off">−{n - e}만 원</td></tr>'
        for c, n, e in EVENT_PRICES)
    return f'''<!-- EVENT:START -->
  <section class="event js-event" id="event" aria-labelledby="evTitle">
    <div class="wrap">
      <div class="ev-card">
        <div class="ev-intro">
          <p class="ev-badge">원앤온리PT 5주년 기념 이벤트</p>
          <h2 id="evTitle">“원앤온리는 왜 할인 안 해요?”</h2>
          <p class="ev-sub">매달 들었던 질문. 그래서, 준비했습니다.</p>
          <p class="ev-big">최대 <em>{EVENT_MAX_OFF}만 원</em> 할인</p>
          <p class="ev-meta"><b>11월 30일까지</b><span>선착순 20명 한정</span><span class="ev-dday" id="evDday" hidden></span></p>
          <p class="ev-for"><b>허리 · 무릎 · 어깨 · 관절 통증 · 수술 후 재활 · 다이어트</b><br>내 몸 상태에 맞춘 1:1 평가 기반 재활 트레이닝</p>
          <div class="ev-actions">
            <a class="btn btn-cta ev-btn" href="{book}" target="_blank" rel="noopener" data-track="lead" data-method="naver_booking" data-location="event">무료 근신경 기능평가·상담 예약하기</a>
            <a class="btn btn-line" href="tel:050714710290" data-track="lead" data-method="phone" data-location="event">전화 0507-1471-0290</a>
          </div>
        </div>
        <div class="ev-table">
          <table class="ev-price">
            <caption>신동훈 대표 1:1 수업 이벤트가</caption>
            <thead><tr><th scope="col">횟수</th><th scope="col">정상가</th><th scope="col">이벤트가</th><th scope="col">할인</th></tr></thead>
            <tbody>
{rows}
            </tbody>
          </table>
          <ul class="ev-notes">
            <li>신동훈 대표가 직접 진행하는 1:1 개인 수업 기준입니다.</li>
            <li>11월 30일까지 선착순 20명에게 적용되며, 20명이 차면 일찍 마감될 수 있어요.</li>
            <li>첫 방문은 무료 근신경 기능평가와 상담으로 진행합니다.</li>
            <li>부산교대역(1호선) 4번 출구에서 걸어서 5분 이내 · 연제구 명륜로 2번길 7, 삼익퓨처타워상가 306호 (베스킨라빈스·센텀스타마트 건물)</li>
          </ul>
        </div>
      </div>
    </div>
  </section>
  {EVENT_HIDE}
<!-- EVENT:END -->
'''


def event_strip(home_href):
    if not EVENT_ON:
        return ""
    return f'''<!-- EVENT:START -->
<a class="ev-strip js-event" href="{home_href}#event"><b>5주년 기념 이벤트</b> 최대 {EVENT_MAX_OFF}만 원 할인 · 11월 30일까지 선착순 20명 <span aria-hidden="true">→</span></a>
{EVENT_HIDE}
<!-- EVENT:END -->
'''


EVENT_CSS = """
/* ---------- 5주년 이벤트 (11/30까지) ---------- */
.event { padding-block: 24px 8px; }
.ev-card { display: grid; gap: 28px; padding: clamp(22px, 4vw, 44px); border-radius: 24px; background: #164E45; color: #fff; }
@media (min-width: 900px) { .ev-card { grid-template-columns: 1fr 1.05fr; gap: 44px; align-items: start; } }
.ev-badge { display: inline-block; margin: 0 0 14px; padding: 6px 12px; border-radius: 999px; background: rgba(255,255,255,.14); font-size: 14px; font-weight: 700; }
.ev-card h2 { color: #fff; font-size: clamp(28px, 4.6vw, 42px); }
.ev-sub { margin-top: 10px; color: rgba(255,255,255,.82); font-size: 17px; }
.ev-big { margin-top: 18px; font-family: var(--display); font-size: clamp(38px, 6.4vw, 58px); line-height: 1.1; }
.ev-big em { font-style: normal; color: #F2B544; }
.ev-meta { margin-top: 14px; display: flex; flex-wrap: wrap; gap: 8px; }
.ev-meta > * { padding: 6px 12px; border-radius: 8px; background: rgba(255,255,255,.12); font-size: 15px; }
.ev-meta b { background: #F2B544; color: #3A2700; }
.ev-dday { font-family: var(--mono); font-weight: 600; }
.ev-for { margin-top: 18px; color: rgba(255,255,255,.88); font-size: 15.5px; }
.ev-actions { margin-top: 22px; display: flex; flex-wrap: wrap; gap: 8px; }
.ev-btn { min-height: 54px; padding: 10px 24px; line-height: 1.35; text-align: center; font-size: 16.5px; background: #F2B544; color: #3A2700; }
.ev-actions .btn-line { background: transparent; color: #fff; border: 1.5px solid rgba(255,255,255,.4); min-height: 54px; }
.ev-table { background: var(--surface); color: var(--ink); border-radius: 18px; padding: clamp(16px, 2.6vw, 26px); min-width: 0; }
.ev-price { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
.ev-price caption { text-align: left; font-weight: 700; font-size: 15px; color: var(--pine); padding-bottom: 10px; }
.ev-price th, .ev-price td { padding: 11px 6px; border-bottom: 1px solid var(--line); text-align: right; white-space: nowrap; }
.ev-price th:first-child { text-align: left; }
.ev-price thead th { font-size: 13px; font-weight: 500; color: var(--muted); border-bottom: 2px solid var(--ink); }
.ev-price tbody th { font-weight: 700; }
.ev-was { color: var(--muted); font-size: 15px; }
.ev-now { font-family: var(--display); font-size: 21px; color: var(--pine); }
.ev-off { font-size: 14px; font-weight: 700; color: #B4471B; }
.ev-notes { margin: 14px 0 0; padding-left: 18px; color: var(--muted); font-size: 13.5px; line-height: 1.65; display: grid; gap: 4px; }
@media (max-width: 480px) {
  .ev-price th, .ev-price td { padding: 10px 4px; }
  .ev-now { font-size: 19px; }
  .ev-btn, .ev-actions .btn-line { width: 100%; }
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .ev-off { color: #F59E6B; } }
:root[data-theme="dark"] .ev-off { color: #F59E6B; }
.ev-strip { display: block; padding: 10px 20px; text-align: center; background: #164E45; color: #fff; text-decoration: none; font-size: 14.5px; line-height: 1.5; }
.ev-strip b { color: #F2B544; margin-right: 6px; }
.ev-strip:hover { text-decoration: underline; }
"""
