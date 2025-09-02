// enable-brand-spine.js — anchors the vertical spine to the hero card
(() => {
  const root = document.getElementById('fc-hero');
  if (!root) return;
  const frame = root.querySelector('.fc-hero-card');
  const spine = root.querySelector('.brand-spine');
  if (!frame || !spine) return;

  const position = () => {
    const r = frame.getBoundingClientRect();
    const left = r.left + window.scrollX;
    // Stick just outside the left edge on wide screens
    spine.style.left = `calc(${Math.max(0, left)}px - 1.6rem)`;
  };
  position();
  window.addEventListener('resize', position, { passive: true });
})();
