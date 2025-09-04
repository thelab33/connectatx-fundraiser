(function () {
  const confetti = (opts = {}) => {
    try {
      if (window.confetti) {
        window.confetti({
          particleCount: 120,
          spread: 75,
          origin: { y: 0.3 },
          ...opts,
        });
      }
    } catch (e) {}
  };
  const toast = (msg) => {
    try {
      document.dispatchEvent(new CustomEvent("fc:toast", { detail: { msg } }));
    } catch (e) {}
  };

  document.addEventListener("fc:vip:hit", (ev) => {
    const tier = (ev.detail && ev.detail.tier) || "VIP";
    confetti();
    toast(`🥇 ${tier} Sponsor unlocked! Thank you for powering our season.`);
  });

  // Meter live-update hook (raised, goal or pct)
  document.addEventListener("fc:meter:update", (ev) => {
    const d = ev.detail || {};
    if (typeof d.raised === "number") {
      const el = document.getElementById("hdr-raised");
      if (el) el.textContent = `$${d.raised.toLocaleString()}`;
    }
    if (typeof d.goal === "number") {
      const el = document.getElementById("hdr-goal");
      if (el) el.textContent = `$${d.goal.toLocaleString()}`;
    }
    if (typeof d.pct === "number") {
      const el = document.getElementById("hdr-pct");
      if (el) el.textContent = `${d.pct.toFixed(0)}%`;
      const sr = document.getElementById("hdr-sr");
      if (sr) sr.textContent = `${d.pct.toFixed(0)}% to goal`;
    }
  });
})();
