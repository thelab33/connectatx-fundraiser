/* FundChamps — UI helpers (safe, minimal) */
(function () {
  const root = document.documentElement;
  const reduced = window.matchMedia?.(
    "(prefers-reduced-motion: reduce)",
  )?.matches;
  const saveData = navigator.connection && navigator.connection.saveData;
  if (reduced || saveData) root.classList.add("fc-reduced");
})();

// Live meter updates for any .fc-meter in DOM
(function () {
  function update(el, raised, goal) {
    const t = el.querySelector(".track");
    const f = el.querySelector(".fill");
    const pTxt = el.querySelector(".pct");
    const p = Math.max(0, Math.min(100, goal ? (raised / goal) * 100 : 0));
    if (f) f.style.inlineSize = p.toFixed(1) + "%";
    if (pTxt) pTxt.textContent = p.toFixed(0) + "%";
    if (t) t.setAttribute("aria-valuenow", p.toFixed(1));
  }
  document.addEventListener(
    "fc:meter:update",
    (e) => {
      const d = e.detail || {};
      document
        .querySelectorAll(".fc-meter")
        .forEach((el) => update(el, +d.raised || 0, +d.goal || 0));
    },
    { passive: true },
  );
})();
