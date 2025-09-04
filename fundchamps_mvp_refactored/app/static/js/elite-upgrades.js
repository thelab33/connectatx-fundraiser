(() => {
  try {
    const d = document,
      rail = d.createElement("div");
    rail.id = "fc-mini-rail";
    rail.innerHTML = "<b></b>";
    d.addEventListener("DOMContentLoaded", () => d.body.appendChild(rail), {
      once: 1,
    });
    const fill = rail.firstElementChild;
    const pct = () => {
      const m = window.getHeroMeter?.();
      if (m && m.goal) {
        return Math.min(100, Math.max(0, 100 * (m.raised / m.goal)));
      }
      const t = d.getElementById("fc-pct");
      return t ? parseFloat(t.textContent) || 0 : 0;
    };
    const set = (p) => {
      const v = (+p || 0).toFixed(1) + "%";
      fill.style.setProperty("--w", v);
      fill.style.width = v;
    };
    const boot = () => set(pct());
    if (d.readyState != "loading") boot();
    else d.addEventListener("DOMContentLoaded", boot, { once: 1 });
    addEventListener("fc:funds:update", (e) => {
      const s = e.detail || {};
      if (typeof s.raised === "number" && typeof s.goal === "number") {
        set(Math.min(100, Math.max(0, 100 * (s.raised / s.goal))));
      }
    });
    const t = d.getElementById("fc-ticker");
    if ("IntersectionObserver" in window && t) {
      new IntersectionObserver(
        ([o]) => {
          d.documentElement.style.setProperty(
            "--ticker",
            o.isIntersecting ? "running" : "paused",
          );
        },
        { threshold: 0.1 },
      ).observe(t);
    }
    const meta = (() => {
      let m = d.querySelector("meta[name=theme-color]");
      if (!m) {
        m = d.createElement("meta");
        m.setAttribute("name", "theme-color");
        d.head.appendChild(m);
      }
      return m;
    })();
    const col = (
      getComputedStyle(d.documentElement).getPropertyValue(
        "--fc-hero-accent",
      ) || "#facc15"
    ).trim();
    meta.setAttribute("content", col);
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker
        .register("/static/js/elite-sw.js")
        .catch(() => {});
    }
  } catch (e) {}
})();
