(function () {
  const mountId = "fc-toasts";
  function ensureMount() {
    let m = document.getElementById(mountId);
    if (!m) {
      m = document.createElement("div");
      m.id = mountId;
      m.setAttribute("aria-live", "polite");
      m.style.position = "fixed";
      m.style.right = "1rem";
      m.style.bottom = "1rem";
      m.style.zIndex = "2147483647";
      document.body.appendChild(m);
    }
    return m;
  }
  function show(msg) {
    const m = ensureMount();
    const n = document.createElement("div");
    n.textContent = msg;
    n.role = "status";
    n.style.padding = "12px 14px";
    n.style.marginTop = "8px";
    n.style.borderRadius = "12px";
    n.style.background = "rgba(250, 204, 21, 0.95)"; // gold-ish
    n.style.color = "#111";
    n.style.fontWeight = "600";
    n.style.boxShadow = "0 10px 30px rgba(0,0,0,.35)";
    n.style.maxWidth = "320px";
    n.style.pointerEvents = "auto";
    m.appendChild(n);
    setTimeout(() => {
      n.style.opacity = "0";
      n.style.transition = "opacity .3s";
    }, 2500);
    setTimeout(() => {
      n.remove();
    }, 3000);
  }
  document.addEventListener("fc:toast", (e) =>
    show((e.detail && e.detail.msg) || "Done"),
  );
})();
