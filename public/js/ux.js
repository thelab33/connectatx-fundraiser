// Accessibility / UX helpers
(() => {
  // Add keyboard-only focus class
  let usingMouse = false;
  document.addEventListener("mousedown", () => (usingMouse = true));
  document.addEventListener("keydown", () => (usingMouse = false));
  document.addEventListener("focusin", (e) => {
    if (!usingMouse) e.target.classList.add("focus-visible");
  });
  document.addEventListener("focusout", (e) =>
    e.target.classList.remove("focus-visible"),
  );

  // Respect reduced motion: pause any marquee/auto-advance with [data-auto]
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce)
    document.querySelectorAll("[data-auto]").forEach((el) => {
      el.dataset.auto = "off";
    });

  // Simple countdown utility (any .countdown[data-end])
  const targets = document.querySelectorAll(".countdown[data-end]");
  function tick() {
    targets.forEach((el) => {
      const end = new Date(el.dataset.end).getTime();
      const left = Math.max(0, end - Date.now());
      const d = Math.floor(left / 86400000);
      const h = Math.floor((left % 86400000) / 3600000);
      const m = Math.floor((left % 3600000) / 60000);
      el.textContent = left === 0 ? "Event started" : `${d}d ${h}h ${m}m`;
      el.setAttribute("aria-live", "polite");
    });
  }
  tick();
  setInterval(tick, 60000);
})();
