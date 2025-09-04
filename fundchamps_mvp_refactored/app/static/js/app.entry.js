/* eslint-disable no-empty */
// app/static/js/app.entry.js
// FundChamps / Connect ATX Elite
// - CSP-safe, production-ready
// - Hardened fetch (CSRF + headers, same-origin only)
// - Optional HTMX, Alpine.js, BroadcastChannel
// - Nike/Apple-level polish

(() => {
  "use strict";
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
    (document.cookie.match(new RegExp("(^|;\\s*)" + k + "=([^;]*)")) ||
      [])[2] || "";

  const csrfToken = () =>
    document.querySelector('meta[name="csrf-token"]')?.content ||
    getCookie("csrf_token") ||
    "";

  // Broadcast channel (optional)
  let bus = null;
  try {
    bus = new BroadcastChannel("fc_ui");
  } catch {}

  // Small DOM/query helpers
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Same-origin test (safe for Request/URL/string)
  const isSameOrigin = (input) => {
    try {
      const u =
        typeof input === "string"
          ? new URL(input, location.href)
          : input instanceof Request
            ? new URL(input.url, location.href)
            : input?.url
              ? new URL(input.url, location.href)
              : null;
      return !u || u.origin === location.origin;
    } catch {
      return false;
    }
  };

  // Public FC namespace
  const fc = {
    env: ENV,
    dev: DEV,
    bus,
    csrf: csrfToken,
    on: (type, fn, opts) => {
      window.addEventListener(type, fn, opts);
      return () => window.removeEventListener(type, fn, opts);
    },
    emit: (type, detail) =>
      window.dispatchEvent(new CustomEvent(type, { detail })),
  };
  window.fc = Object.assign(window.fc || {}, fc);

  /* ---------- Fetch hardening ---------- */
  const _fetch = window.fetch ? window.fetch.bind(window) : null;

  // Helper: JSON fetch with errors surfaced
  async function fetchJSON(input, init = {}) {
    const res = await window.fetch(input, init);
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      const err = new Error(`HTTP ${res.status} ${res.statusText}`);
      err.status = res.status;
      err.body = text;
      throw err;
    }
    // 204 or empty → null
    if (res.status === 204) return null;
    const ct = res.headers.get("content-type") || "";
    return ct.includes("application/json") ? res.json() : res.text();
  }
  window.fc.fetchJSON = fetchJSON;

  if (_fetch) {
    window.fetch = (input, init = {}) => {
      const headers = new Headers(init.headers || {});
      const method = String(init.method || "GET").toUpperCase();
      const same = isSameOrigin(input);

      // Accept header is harmless; prefer JSON then HTML for partials
      if (!headers.has("Accept")) {
        headers.set("Accept", "application/json, text/html;q=0.9, */*;q=0.8");
      }

      // Only tag X-Requested-With for same-origin to avoid CORS surprises
      if (same && !headers.has("X-Requested-With")) {
        headers.set("X-Requested-With", "XMLHttpRequest");
      }

      // CSRF only for mutating same-origin requests
      const mutating = !["GET", "HEAD", "OPTIONS", "TRACE"].includes(method);
      if (same && mutating && !headers.has("X-CSRFToken")) {
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
        if (isSameOrigin(e.detail.path)) {
          e.detail.headers["X-Requested-With"] = "XMLHttpRequest";
          const tok = csrfToken();
          if (tok) e.detail.headers["X-CSRFToken"] = tok;
        }
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
        .then((m) =>
          typeof m.default === "function" ? m.default() : undefined,
        )
        .catch((err) => {
          if (DEV) console.warn(`↪️ ${name} skipped:`, err?.message || err);
        });

    // staged order: site → sponsor → fundraiser
    await Promise.allSettled([
      boot("./site.js", "site.js"),
      boot("./sponsor.js", "sponsor.js"),
      boot("./fundraiser.js", "fundraiser.js"),
    ]);

    // Alpine is optional
    try {
      const { default: Alpine } = await import(
        /* webpackChunkName:"alpine" */ "alpinejs"
      );
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
      console.warn("✅ app.entry booted", {
        env: ENV,
        serverTiming: nav?.serverTiming || [],
      });
    } else {
      // Keep a single line for log sampling in prod
      console.warn("✅ app.entry.js loaded");
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }

  /* ---------- HMR (vite/webpack) ---------- */
  try {
    if (import.meta && import.meta.hot) {
      import.meta.hot.accept?.();
      if (DEV) console.warn("🔁 HMR active");
    }
  } catch {}
})();
