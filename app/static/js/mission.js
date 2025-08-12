// static/js/mission.js
(function () {
  const root = document.getElementById('elite-mission');
  if (!root) return;

  // Tooltip delegation (hover + focus)
  const badgeList = root.querySelector('[data-badge-list]');
  function handleTipToggle(e) {
    const badge = e.target.closest('[data-badge]');
    if (!badge || !badgeList || !badgeList.contains(badge)) return;
    const tip = badge.querySelector('[data-badge-tip]');
    if (!tip) return;
    const show = e.type === 'mouseover' || e.type === 'focusin';
    if (badge.dataset.tooltip) tip.textContent = badge.dataset.tooltip;
    tip.setAttribute('aria-hidden', show ? 'false' : 'true');
    tip.style.opacity = show ? '1' : '0';
    tip.style.pointerEvents = show ? 'auto' : 'none';
  }
  if (badgeList) {
    badgeList.addEventListener('mouseover', handleTipToggle, true);
    badgeList.addEventListener('mouseout', handleTipToggle, true);
    badgeList.addEventListener('focusin', handleTipToggle, true);
    badgeList.addEventListener('focusout', handleTipToggle, true);
  }

  // Counter animation on view
  const counters = Array.from(root.querySelectorAll('[data-counter]'));
  if (counters.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          animateCounter(entry.target);
          io.unobserve(entry.target);
        });
      },
      { rootMargin: '0px 0px -10% 0px', threshold: 0.25 },
    );
    counters.forEach((c) => io.observe(c));
  }

  function parseTarget(text) {
    const clean = String(text || '')
      .trim()
      .replace(/,/g, '')
      .replace(/\+$/, '');
    const mult = /k$/i.test(clean) ? 1_000 : /m$/i.test(clean) ? 1_000_000 : 1;
    const num = parseFloat(clean.replace(/[kKmM]$/, '')) || 0;
    return num * mult;
  }

  function animateCounter(container) {
    const node = container.querySelector('[data-counter-value]');
    if (!node) return;
    const raw = node.getAttribute('data-target') || node.textContent || '0';
    const target = parseTarget(raw);
    const isInt = Number.isInteger(target);
    const start = performance.now();
    const dur = 900;
    (function frame(now) {
      const t = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - t, 3);
      const val = target * eased;
      node.textContent = isInt ? Math.round(val).toLocaleString() : val.toFixed(1);
      if (t < 1) requestAnimationFrame(frame);
    })(start);
  }
})();
