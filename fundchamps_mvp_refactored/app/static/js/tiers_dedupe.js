/*! Dev helper: hides exact duplicate #tiers sections (same markup) */
(function () {
  document.addEventListener("DOMContentLoaded", function () {
    const sections = Array.from(
      document.querySelectorAll('[data-dedupe-key="tiers"]'),
    );
    if (sections.length <= 1) return;
    const norm = (s) => s.replace(/\s+/g, " ").trim();
    const seen = new Set();
    for (const el of sections) {
      const key = norm(el.innerHTML);
      if (seen.has(key)) {
        el.style.display = "none";
        el.setAttribute("data-duplicate", "true");
      } else seen.add(key);
    }
    console.warn(
      "[tiers_dedupe] duplicates hidden:",
      sections.length - seen.size,
    );
  });
})();
