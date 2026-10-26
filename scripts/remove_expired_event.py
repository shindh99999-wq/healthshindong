"""기간이 지난 이벤트 영역(<!-- EVENT:START --> ~ <!-- EVENT:END -->)을 모든 페이지에서 지웁니다.
매일 아침 자동 업데이트에서 실행됩니다. 기간 안이면 아무것도 하지 않습니다."""
import re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_src"))
from event import EVENT_END_ISO  # noqa: E402

now = datetime.now(timezone(timedelta(hours=9)))
if now < datetime.fromisoformat(EVENT_END_ISO):
    print("이벤트 기간 중:", EVENT_END_ISO, "까지")
    sys.exit(0)
pat = re.compile(r"[ \t]*<!-- EVENT:START -->.*?<!-- EVENT:END -->\n?", re.S)
for f in list(ROOT.glob("*.html")) + list(ROOT.glob("*/index.html")):
    s = f.read_text(encoding="utf-8")
    t = pat.sub("", s)
    if t != s:
        f.write_text(t, encoding="utf-8")
        print("이벤트 삭제:", f.relative_to(ROOT))
