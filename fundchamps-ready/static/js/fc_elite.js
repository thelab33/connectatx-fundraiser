// minimal helpers for demo
window.openDonationModal =
  window.openDonationModal ||
  function (opts) {
    try {
      console.log("openDonationModal", opts);
    } catch (e) {}
  };
window.addEventListener("fc:meter:update", (e) => {
  const pct =
    e.detail && e.detail.goal > 0
      ? Math.min(100, Math.max(0, (100 * e.detail.raised) / e.detail.goal))
      : 0;
  const fill = document.getElementById("hero-fill");
  if (fill) fill.style.width = pct.toFixed(1) + "%";
});
