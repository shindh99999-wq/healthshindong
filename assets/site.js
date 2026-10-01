(function () {
  // 클릭 통계: 채널 이동(click_platform), 상담 버튼(generate_lead), 상담 섹션 이동(lead_intent), 지도(click_map)
  function send(name, params) {
    try { if (typeof gtag === 'function') gtag('event', name, params); } catch (e) {}
  }
  document.addEventListener('click', function (e) {
    var el = e.target.closest('[data-track]');
    if (!el) return;
    var t = el.dataset.track, loc = el.dataset.location || '';
    if (t === 'platform') send('click_platform', { platform: el.dataset.platform, link_location: loc });
    else if (t === 'lead') send('generate_lead', { method: el.dataset.method, link_location: loc });
    else if (t === 'lead_intent') send('lead_intent', { link_location: loc });
    else if (t === 'map') send('click_map', { platform: el.dataset.platform });
  });

  // 주소 복사
  var btn = document.getElementById('copyAddr');
  function toast(msg) {
    var d = document.createElement('div'); d.className = 'toast'; d.textContent = msg;
    document.body.appendChild(d); setTimeout(function () { d.remove(); }, 1800);
  }
  if (btn) btn.addEventListener('click', function () {
    var text = btn.dataset.copy;
    var done = function () { toast('주소를 복사했어요'); };
    var fallback = function () {
      var r = document.createRange(); r.selectNodeContents(document.getElementById('addr'));
      var s = getSelection(); s.removeAllRanges(); s.addRange(r); toast('주소를 선택했어요. 복사해서 쓰세요');
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, fallback);
    else fallback();
  });
})();
