/* app/static/js/fc_prestige.js — micro‑UX & live sync (no dependencies) */
(function () {
  const bus = (window.fc = window.fc || {});
  bus.emit = (n, d = {}) =>
    document.dispatchEvent(new CustomEvent(n, { detail: d }));
  bus.on = (n, fn) => document.addEventListener(n, fn);

  // Sticky header shadow
  const header =
    document.querySelector('header.header, header[data-fc="hdr"]') ||
    document.querySelector("header");
  if (header) {
    const sticky = () =>
      header.classList.toggle("fc-sticky-shadow", window.scrollY > 4);
    sticky();
    window.addEventListener("scroll", sticky, { passive: true });
  }

  // Reveal on view
  const io = new IntersectionObserver(
    (ents) => {
      ents.forEach(
        (e) => e.isIntersecting && e.target.classList.add("is-visible"),
      );
    },
    { threshold: 0.12 },
  );
  document.querySelectorAll(".fc-reveal").forEach((el) => io.observe(el));

  // CountUp for metrics
  function countUp(el) {
    const end = parseFloat(el.getAttribute("data-countup") || "0");
    const dur = parseInt(el.getAttribute("data-countup-ms") || "1100", 10);
    const start = performance.now();
    function tick(t) {
      const p = Math.min(1, (t - start) / dur);
      const v = Math.floor(end * (0.5 - Math.cos(Math.PI * p) / 2)); // easeInOut
      el.textContent = Number.isFinite(end) ? v.toLocaleString() : end;
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }
  document.querySelectorAll("[data-countup]").forEach(countUp);

  // Mini header fundraiser meter
  function updateHeaderMeter(data) {
    const raised = Number(data.raised || data.funds_raised || 0);
    const goal = Number(data.goal || data.fundraising_goal || 1);
    const pct = Math.max(0, Math.min(100, (raised / goal) * 100));
    const elBar = document.querySelector("#hdr-meter .fill");
    const elPct = document.querySelector("#hdr-pct");
    const elR = document.querySelector("#hdr-raised");
    const elG = document.querySelector("#hdr-goal");
    if (elBar) elBar.style.width = pct.toFixed(1) + "%";
    if (elPct) elPct.textContent = pct.toFixed(1) + "%";
    if (elR) elR.textContent = "$" + Math.round(raised).toLocaleString();
    if (elG) elG.textContent = "$" + Math.round(goal).toLocaleString();
  }

  window.fc = window.fc || {};
  window.fc.on = (n, fn) => document.addEventListener(n, fn);
  document.addEventListener("fc:funds:update", (e) =>
    updateHeaderMeter(e.detail || {}),
  );

  // Optional autostats
  const cfg = window.FC_CONFIG || {};
  const STATS_URL = cfg.stats_url || "/demo/stats";
  const POLL_MS = cfg.poll_ms || 15000;
  const AUTOSTATS = "autostats" in cfg ? !!cfg.autostats : true;

  async function fetchStats() {
    try {
      const res = await fetch(STATS_URL, { credentials: "same-origin" });
      const j = await res.json();
      document.dispatchEvent(new CustomEvent("fc:funds:update", { detail: j }));
    } catch (err) {
      void err; /* no-op */
    }
  }
  if (AUTOSTATS) {
    fetchStats();
    setInterval(fetchStats, POLL_MS);
  }

  // VIP confetti (lightweight)
  window.fcConfetti = function fireConfetti() {
    if (!window.confetti) return;
    window.confetti({ particleCount: 120, spread: 70, origin: { y: 0.6 } });
  };
})();
