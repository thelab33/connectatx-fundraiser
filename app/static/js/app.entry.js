/* eslint-disable no-empty */
// app/static/js/app.entry.js
// FundChamps / Connect ATX Elite
// - CSP-safe, production-ready
// - Hardened fetch (CSRF + headers)
// - Optional HTMX, Alpine.js, BroadcastChannel
// - Nike/Apple-level polish

(() => {
  if (window.__FC_APP_INIT__) return;
  window.__FC_APP_INIT__ = true;

  /* ---------- Env / helpers ---------- */
  const html = document.documentElement;
  html.classList.add("js");
  html.classList.remove("no-js");
  html.setAttribute("data-fc-app", "true");

  const ENV = html.getAttribute("data-env") || window.APP_ENV || "production";
  const DEV = /dev|local/.test(String(ENV).toLowerCase());

  const getCookie = (k) =>
    (document.cookie.match(new RegExp("(^|;\\s*)" + k + "=([^;]*)")) || [])[2] || "";

  const csrfToken = () => getCookie("csrf_token");

  let bus = null;
  try { bus = new BroadcastChannel("fc_ui"); } catch { /* ignore */ }

  window.fc = Object.assign(window.fc || {}, {
    env: ENV,
    dev: DEV,
    bus,
    csrf: csrfToken,
    on: (type, fn, opts) => window.addEventListener(type, fn, opts),
    emit: (type, detail) => window.dispatchEvent(new CustomEvent(type, { detail })),
  });

  /* ---------- Fetch hardening ---------- */
  const _fetch = window.fetch ? window.fetch.bind(window) : null;
  if (_fetch) {
    window.fetch = (input, init = {}) => {
      const headers = new Headers(init.headers || {});
      if (!headers.has("Accept")) {
        headers.set("Accept", "application/json, text/html;q=0.9, */*;q=0.8");
      }
      if (!headers.has("X-Requested-With")) {
        headers.set("X-Requested-With", "XMLHttpRequest");
      }
      const method = String(init.method || "GET").toUpperCase();
      const sameOrigin = typeof input === "string" ? input.startsWith("/") : true;
      if (sameOrigin && !["GET", "HEAD", "OPTIONS", "TRACE"].includes(method) && !headers.has("X-CSRFToken")) {
        const tok = csrfToken();
        if (tok) headers.set("X-CSRFToken", tok);
      }
      return _fetch(input, { credentials: "same-origin", ...init, headers });
    };
  }

  /* ---------- HTMX (optional) ---------- */
  if (window.htmx) {
    try {
      window.htmx.config.withCredentials = true;
      window.htmx.config.scrollBehavior = "instant";
      document.body.addEventListener("htmx:configRequest", (e) => {
        e.detail.headers["X-Requested-With"] = "XMLHttpRequest";
        const tok = csrfToken();
        if (tok) e.detail.headers["X-CSRFToken"] = tok;
      });
    } catch {}
  }

  /* ---------- Error boundaries ---------- */
  window.addEventListener("error", (e) => {
    if (DEV) console.error("⛑️ Uncaught:", e.error || e.message);
    window.fc.emit("fc:error", { type: "error", error: e.error || e.message });
  });
  window.addEventListener("unhandledrejection", (e) => {
    if (DEV) console.error("⛑️ Rejection:", e.reason);
    window.fc.emit("fc:error", { type: "rejection", error: e.reason });
  });

  /* ---------- App start ---------- */
  const start = async () => {
    const boot = (path, name) =>
      import(/* webpackChunkName: "[request]" */ path)
        .then((m) => (typeof m.default === "function" ? m.default() : undefined))
        .catch((err) => {
          if (DEV) console.warn(`↪️ ${name} skipped:`, err?.message || err);
        });

    // staged order: site → sponsor → fundraiser
    await Promise.allSettled([
      boot("./site.js", "site.js"),
      boot("./sponsor.js", "sponsor.js"),
      boot("./fundraiser.js", "fundraiser.js"),
    ]);

    try {
      const { default: Alpine } = await import(/* webpackChunkName:"alpine" */ "alpinejs");
      window.Alpine = Alpine;
      Alpine.store?.("fc", { env: ENV, dev: DEV, csrf: csrfToken() });
      const initAlpine = () => Alpine.start();
      (window.requestIdleCallback || setTimeout)(initAlpine, 1);
    } catch (err) {
      if (DEV) console.warn("ℹ️ Alpine not present:", err?.message || err);
    }

    window.fc.emit("fc:ready", { env: ENV, dev: DEV });
    if (DEV) {
      const nav = performance.getEntriesByType?.("navigation")?.[0];
      console.warn("✅ app.entry booted", { env: ENV, serverTiming: nav?.serverTiming || [] });
    } else {
      console.warn("✅ app.entry.js loaded");
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }

  /* ---------- HMR (vite/webpack) ---------- */
  if (import.meta && import.meta.hot) {
    import.meta.hot.accept?.();
    if (DEV) console.warn("🔁 HMR active");
  }
})();

