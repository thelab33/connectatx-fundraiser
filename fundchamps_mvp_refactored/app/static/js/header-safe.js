(() => {
  try {
    const d = document,
      header =
        d
          .querySelector("#site-header,[data-sticky-header]")
          ?.closest("header") || d.querySelector("header");
    // shrink on scroll (IO when possible)
    const sentinel =
      d.getElementById("site-header-sentinel") || d.createElement("div");
    if (!sentinel.isConnected) {
      sentinel.id = "site-header-sentinel";
      header?.before(sentinel);
    }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(
        ([e]) => {
          header?.classList.toggle("is-shrunk", !e.isIntersecting);
        },
        { rootMargin: "-56px 0px 0px 0px" },
      ).observe(sentinel);
    }
    // mini meter sync
    const fill =
      d.querySelector("#hdr-meter .fill") || d.querySelector("#hdr-bar");
    const pctLbl = d.querySelector("#hdr-meter [data-hdr-pct],#hdr-pct");
    const raisedLbl = d.querySelector("#hdr-raised");
    const goalLbl = d.querySelector("#hdr-goal");
    const nf = new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 });
    const fmt$ = (n) => "$" + nf.format(Math.round(+n || 0));
    function setMeter(raised, goal) {
      if (!(goal > 0)) return;
      const p = Math.max(0, Math.min(100, (raised / goal) * 100));
      if (fill) fill.style.width = p.toFixed(1) + "%";
      if (pctLbl) pctLbl.textContent = p.toFixed(0) + "%";
      if (raisedLbl) raisedLbl.textContent = fmt$(raised);
      if (goalLbl) goalLbl.textContent = fmt$(goal);
    }
    // listen for the app's live events
    addEventListener(
      "fc:funds:update",
      (e) => {
        const { raised, goal } = e.detail || {};
        if (typeof raised === "number" && typeof goal === "number")
          setMeter(raised, goal);
      },
      { passive: true },
    );
    // initial pull (non-blocking)
    const url = header?.dataset.statsUrl || "/api/stats";
    (async () => {
      try {
        const r = await fetch(url, { headers: { Accept: "application/json" } });
        if (r.ok) {
          const j = await r.json();
          setMeter(j.raised ?? j.funds_raised, j.goal ?? j.fundraising_goal);
        }
      } catch {}
    })();
    // set theme-color to accent for mobile UI
    let meta = d.querySelector("meta[name=theme-color]");
    if (!meta) {
      meta = d.createElement("meta");
      meta.name = "theme-color";
      d.head.appendChild(meta);
    }
    const col = (
      getComputedStyle(d.documentElement).getPropertyValue(
        "--fc-hero-accent",
      ) || "#facc15"
    ).trim();
    meta.setAttribute("content", col);
  } catch (e) {}
})();
