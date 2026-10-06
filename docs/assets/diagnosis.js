/* かんたん診断: #diagnosis 内の選択肢をクリックすると、診断結果を表示する (JS無効時は全項目をそのまま表示) */
(function () {
  var sec = document.getElementById('diagnosis');
  if (!sec) return;
  var boxes = sec.querySelectorAll('.merit-box');
  if (!boxes.length) return;

  var css = document.createElement('style');
  css.textContent =
    '.diag-choices .merit-box{cursor:pointer;margin:0;transition:transform .1s}' +
    '.diag-choices .merit-box:hover{transform:translateY(-2px)}' +
    '.diag-choices .merit-box:focus-visible{outline:3px solid #f2a900;outline-offset:2px}' +
    '.diag-choices .merit-box.is-selected{background:#fff3c4;outline:3px solid #f2a900;outline-offset:2px}' +
    '.diag-choices .merit-box p{display:none}' +
    '.diag-choices .merit-box h3::after{content:" ▶";font-size:.8em}' +
    '.diag-choices .merit-box.is-selected h3::after{content:" ✔"}' +
    '.diag-result{margin-top:16px;padding:16px 18px;border:2px solid #2a2a2a;border-radius:14px;background:#fff;box-shadow:4px 4px 0 #2a2a2a}' +
    '.diag-result[hidden]{display:none}' +
    '.diag-result h3{margin:0 0 8px;font-size:1.05rem}' +
    '.diag-result p{margin:0 0 8px}' +
    '.diag-hint{margin:0 0 12px}';
  document.head.appendChild(css);

  var wrap = boxes[0].parentNode;
  wrap.classList.add('diag-choices');
  wrap.setAttribute('role', 'radiogroup');
  wrap.setAttribute('aria-label', 'いちばん当てはまるものを選んでください');

  var result = document.createElement('div');
  result.className = 'diag-result';
  result.setAttribute('aria-live', 'polite');
  result.hidden = true;
  wrap.parentNode.insertBefore(result, wrap.nextSibling);

  function select(box) {
    boxes.forEach(function (b) { b.classList.remove('is-selected'); b.setAttribute('aria-checked', 'false'); });
    box.classList.add('is-selected');
    box.setAttribute('aria-checked', 'true');
    var title = box.querySelector('h3').textContent.replace(/[「」]/g, '');
    var body = box.querySelector('p').innerHTML;
    var more = document.getElementById('services') || document.getElementById('points') || document.getElementById('types');
    var link = more ? '<p><a href="#' + more.id + '">比較表で候補を見る ↓</a></p>' : '';
    result.innerHTML = '<h3>診断結果：' + title + '</h3><p>' + body + '</p>' + link;
    result.hidden = false;
  }

  boxes.forEach(function (box) {
    box.setAttribute('role', 'radio');
    box.setAttribute('aria-checked', 'false');
    box.tabIndex = 0;
    box.addEventListener('click', function (e) {
      if (e.target.closest('a')) return;
      select(box);
    });
    box.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(box); }
    });
  });
})();
