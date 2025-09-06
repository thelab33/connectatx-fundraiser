/* eslint-disable no-empty */
// app/static/js/app.entry.js
// FundChamps / Connect ATX Elite — P2P-tailored entry
// CSP-safe, production-ready. No globals leaked except `window.fc` (+ alias `window.FC`).

(() => {
  "use strict";
  if (window.__FC_APP_INIT__) return;
  window.__FC_APP_INIT__ = true;

  /* ───────────────────────────── Env / prefs ───────────────────────────── */
  const html = document.documentElement;
  html.classList.add("js");
  html.classList.remove("no-js");
  html.setAttribute("data-fc-app", "true");

  const ENV = html.getAttribute("data-env") || window.APP_ENV || "production";
  const DEV = /dev|local/.test(String(ENV).toLowerCase());

  const mql = (q) => !!(window.matchMedia && window.matchMedia(q).matches);
  const prefers = {
    reducedMotion: mql("(prefers-reduced-motion: reduce)"),
    reducedData:
      !!(navigator.connection &&
        (navigator.connection.saveData ||
          String(navigator.connection.effectiveType || "").includes("2g"))),
    highContrast: mql("(prefers-contrast: more)"),
  };
  if (prefers.reducedMotion || prefers.reducedData) html.classList.add("fc-reduced");

  /* ───────────────────────────── DOM helpers ───────────────────────────── */
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const once = (type, fn, opts) => {
    const wrapped = (e) => { try { fn(e); } finally { window.removeEventListener(type, wrapped, opts); } };
    window.addEventListener(type, wrapped, opts);
  };
  const idle = (fn, timeout = 1200) =>
    "requestIdleCallback" in window ? window.requestIdleCallback(fn, { timeout }) : setTimeout(fn, 0);
  const raf = (fn) => requestAnimationFrame(fn);
  const defer = (fn) => idle(() => raf(fn));

  /* ───────────────────────────── CSP nonce ─────────────────────────────── */
  let NONCE = $('meta[name="csp-nonce"]')?.content || "";
  if (!NONCE) {
    try { NONCE = document.currentScript?.nonce || ""; } catch {}
  }
  const withNonce = (el) => { if (NONCE) el.setAttribute("nonce", NONCE); return el; };

  /* ───────────────────────────── Cookies / CSRF ────────────────────────── */
  const getCookie = (k) => {
    try {
      const m = document.cookie.match(new RegExp("(^|;\\s*)" + k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "=([^;]*)"));
      return m ? decodeURIComponent(m[2]) : "";
    } catch { return ""; }
  };
  const csrfToken = () => $('meta[name="csrf-token"]')?.content || getCookie("csrf_token") || "";

  /* ───────────────────────────── Events bus ────────────────────────────── */
  let bus = null;
  try {
    bus = new BroadcastChannel("fc_ui");
    bus.onmessage = (e) => {
      const d = e?.data;
      if (d && d.t) emit(d.t, d);
    };
  } catch {}
  const emit = (type, detail) => window.dispatchEvent(new CustomEvent(type, { detail }));
  const on = (type, fn, opts) => { window.addEventListener(type, fn, opts); return () => window.removeEventListener(type, fn, opts); };

  /* ───────────────────────────── URL & origin ──────────────────────────── */
  const isSameOrigin = (input) => {
    try {
      const u =
        typeof input === "string" ? new URL(input, location.href)
        : input instanceof Request ? new URL(input.url, location.href)
        : input?.url ? new URL(input.url, location.href)
        : null;
      return !u || u.origin === location.origin;
    } catch { return false; }
  };
  const parseQS = (url = location.href) => Object.fromEntries(new URL(url).searchParams.entries());
  const toQS = (obj) => {
    const usp = new URLSearchParams();
    Object.entries(obj || {}).forEach(([k, v]) => {
      if (v === undefined || v === null || v === "") return;
      if (Array.isArray(v)) v.forEach((vv) => usp.append(k, vv));
      else usp.set(k, String(v));
    });
    return usp.toString();
  };

  /* ───────────────────────────── Storage helpers ───────────────────────── */
  const storage = {
    get(key, fallback = null) {
      try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch { return fallback; }
    },
    set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch {} },
    del(key) { try { localStorage.removeItem(key); } catch {} },
  };
  const ttlGet = (key, fallback = null) => {
    const rec = storage.get(key);
    if (!rec) return fallback;
    if (rec.t && Date.now() > rec.t) { storage.del(key); return fallback; }
    return rec.v ?? fallback;
  };
  const ttlSet = (key, value, ms) => storage.set(key, { v: value, t: ms ? Date.now() + ms : 0 });

  /* ───────────────────────────── Fetch (hardened) ──────────────────────── */
  const _fetch = window.fetch ? window.fetch.bind(window) : null;
  const withTimeout = (ms, upstream) => {
    const local = new AbortController();
    const id = setTimeout(() => local.abort(new DOMException("Timeout", "AbortError")), ms);
    upstream?.addEventListener?.("abort", () => { try { clearTimeout(id); local.abort(upstream.reason); } catch {} }, { once: true });
    return { signal: local.signal, cancel: () => clearTimeout(id) };
  };

  async function fetchSafe(input, init = {}, { timeout = 12000, retries = 0, backoff = 300 } = {}) {
    if (!_fetch) throw new Error("fetch not available");
    const method = String(init.method || "GET").toUpperCase();
    const same = isSameOrigin(input);
    const headers = new Headers(init.headers || {});
    if (!headers.has("Accept")) headers.set("Accept", "application/json, text/html;q=0.9, */*;q=0.8");
    if (same && !headers.has("X-Requested-With")) headers.set("X-Requested-With", "XMLHttpRequest");
    const mutating = !["GET", "HEAD", "OPTIONS", "TRACE"].includes(method);
    if (same && mutating && !headers.has("X-CSRFToken")) {
      const tok = csrfToken(); if (tok) headers.set("X-CSRFToken", tok);
    }

    const upstream = init.signal;
    const { signal, cancel } = withTimeout(timeout, upstream);
    let attempt = 0;

    while (true) {
      try {
        const res = await _fetch(input, { credentials: same ? "same-origin" : "omit", ...init, headers, signal });
        cancel();
        return res;
      } catch (err) {
        const retriable =
          !mutating && same &&
          (err?.name === "AbortError" || /NetworkError|load failed|Failed to fetch/i.test(String(err?.message || "")));
        if (!(retriable && attempt < retries)) throw err;
        const wait = backoff * Math.pow(2, attempt++) + Math.random() * 120;
        await new Promise((r) => setTimeout(r, wait));
      }
    }
  }
  async function fetchJSON(input, init = {}, opts = {}) {
    const res = await fetchSafe(input, init, opts);
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      const err = new Error(`HTTP ${res.status} ${res.statusText}`);
      err.status = res.status; err.body = text; throw err;
    }
    if (res.status === 204) return null;
    const ct = res.headers.get("content-type") || "";
    return ct.includes("application/json") ? res.json() : res.text();
  }
  async function postJSON(url, data, init = {}, opts = {}) {
    const body = data instanceof FormData ? data : JSON.stringify(data ?? {});
    const headers = new Headers(init.headers || {});
    if (!(data instanceof FormData) && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
    return fetchJSON(url, { method: "POST", body, headers, ...init }, opts);
  }

  /* ─────────────────────── Public FC namespace (stable) ────────────────── */
  const fmt = {
    money(v, {
      currency = $("[data-currency]")?.dataset.currency || "USD",
      locale = $("[data-locale]")?.dataset.locale || navigator.language || "en-US",
      maximumFractionDigits = 0,
      notation = "standard",
    } = {}) {
      try { return new Intl.NumberFormat(locale, { style: "currency", currency, maximumFractionDigits, notation }).format(v); }
      catch { return `$${Math.round(+v || 0).toLocaleString()}`; }
    },
    pct(v) { return `${Math.round(+v || 0)}%`; },
  };

  // expose (and alias to window.FC for components that expect it)
  window.fc = Object.assign(window.fc || {}, {
    env: ENV, dev: DEV, prefs: prefers, bus,
    csrf: csrfToken, on, emit, $, $$, idle, raf, defer,
    fetchJSON, postJSON, fetchSafe, fmt,
    util: { parseQS, toQS, storage, ttlGet, ttlSet },
  });
  // Minimal utilities shared by header/about/hero modules:
  Object.assign(window.fc, {
    trapFocus(container) {
      if (!container) return () => {};
      const FOCUS = 'a,button,input,select,textarea,[tabindex]:not([tabindex="-1"])';
      const nodes = () => $$(FOCUS, container).filter((el) => !el.hasAttribute("disabled"));
      const first = () => nodes()[0], last = () => nodes().slice(-1)[0];
      const onKey = (e) => {
        if (e.key !== "Tab") return;
        const f = first(), l = last(); if (!f || !l) return;
        if (e.shiftKey && document.activeElement === f) { e.preventDefault(); l.focus(); }
        else if (!e.shiftKey && document.activeElement === l) { e.preventDefault(); f.focus(); }
      };
      container.addEventListener("keydown", onKey, true);
      return () => container.removeEventListener("keydown", onKey, true);
    },
    decorateLinks(root = document) {
      $$('a[href][data-p2p-propagate="1"]', root).forEach((a) => { a.href = (window.fc&&typeof window.fc.makeTrackedUrl==="function"?window.fc.makeTrackedUrl:(u=>u))(a.href); });
    },
    async handleShare(where = "ui", cfg = {}) {
      try {
        const url = (window.fc&&typeof window.fc.makeTrackedUrl==="function"?window.fc.makeTrackedUrl:(u=>u))(cfg.url || location.href,{ from: where });
        const payload = { title: cfg.title || document.title, text: cfg.text || "Fuel the Season. Fund the Future.", url };
        if (navigator.share) { await navigator.share(payload); return true; }
        await navigator.clipboard.writeText(url); emit("fc:copied", { url, where }); return true;
      } catch { return false; }
    },
  });
  // Alias for legacy callers
  window.FC = window.fc;

  /* Optional: wrap global fetch with our safe version (non-breaking) */
  if (_fetch) window.fetch = (input, init = {}) => fetchSafe(input, init);

  /* ─────────────────────────── External link hardening ─────────────────── */
  const hardenLinks = (root = document) => {
    $$("a[href]", root).forEach((a) => {
      try {
        const href = a.getAttribute("href") || "";
        if (/^(mailto:|tel:|sms:|#)/i.test(href)) return;
        const u = new URL(a.href, location.href);
        const external = u.origin !== location.origin;
        if (external) {
          a.rel = (a.rel || "").split(/\s+/).filter(Boolean).concat(["noopener", "noreferrer"]).join(" ");
          if (!a.target) a.target = "_blank";
        }
      } catch {}
    });
  };

  /* ─────────────────────────── P2P: referral/UTM ───────────────────────── */
  const REF_KEY = "fc_ref_ctx";
  const REF_TTL = 1000 * 60 * 60 * 24 * 7; // 7 days

  const readRefFromURL = () => {
    const q = parseQS();
    const ctx = {
      ref: q.ref || q.player || q.captain || q.athlete || "",
      team: q.team || q.squad || "",
      camp: q.campaign || q.camp || "",
      utm_source: q.utm_source || (q.ref ? "p2p-ref" : ""),
      utm_medium: q.utm_medium || (q.player ? "player" : q.team ? "team" : "site"),
      utm_campaign: q.utm_campaign || q.campaign || "fundchamps",
    };
    return Object.fromEntries(Object.entries(ctx).filter(([, v]) => v));
  };
  const refCtx = Object.assign({}, ttlGet(REF_KEY, {}), readRefFromURL());
  if (Object.keys(refCtx).length) ttlSet(REF_KEY, refCtx, REF_TTL);

  const makeTrackedUrl = (href, extra = {}) => {
    try {
      const u = new URL(href, location.href);
      const incoming = Object.fromEntries(u.searchParams.entries());
      const merged = { ...refCtx, ...incoming, ...extra };
      const qs = toQS(merged);
      u.search = qs ? `?${qs}` : "";
      return u.toString();
    } catch { return href; }
  };

  // Decorate donation anchors/forms and any `[data-p2p-propagate="1"]`
  const decorateDonations = (root = document) => {
    const hasCtx = Object.keys(refCtx).length > 0;
    if (!hasCtx) return;

    $$('a[href][data-donate], a[href*="donate"], a[href*="payments"], a[data-cta="donate"], a[data-p2p-propagate="1"]', root)
      .forEach((a) => { a.href = (window.fc&&typeof window.fc.makeTrackedUrl==="function"?window.fc.makeTrackedUrl:(u=>u))(a.href); });

    $$('form[action*="donate"], form[action*="payments"], form[data-donate]', root).forEach((f) => {
      const ensure = (name, value) => {
        if (!value) return;
        let input = f.querySelector(`input[name="${name}"]`);
        if (!input) { input = document.createElement("input"); input.type = "hidden"; input.name = name; f.appendChild(input); }
        input.value = value;
      };
      Object.entries(refCtx).forEach(([k, v]) => ensure(k, v));
    });
  };

  // Observe DOM changes to keep decoration for dynamic CTAs
  const mo = new MutationObserver((muts) => {
    for (const m of muts) {
      if (m.addedNodes && m.addedNodes.length) {
        m.addedNodes.forEach((n) => {
          if (n.nodeType === 1) {
            decorateDonations(n);
            hardenLinks(n);
            wireShares(n);
            window.fc.decorateLinks(n);
          }
        });
      }
    }
  });

  /* ─────────────────────────── Share wiring (P2P) ──────────────────────── */
  const canShare = !!navigator.share;
  const shareNow = async (payload = {}) => window.fc.handleShare("generic", payload);

  const wireShares = (root = document) => {
    $$("[data-share]", root).forEach((btn) => {
      if (btn.__wiredShare) return;
      btn.__wiredShare = true;
      btn.addEventListener("click", async () => {
        try {
          const raw = btn.getAttribute("data-share");
          const payload = raw ? JSON.parse(raw) : {};
          if (!payload.url) payload.url = location.href;
          const ok = await shareNow(payload);
          if (ok) { const t = btn.textContent; btn.textContent = "Copied!"; setTimeout(() => (btn.textContent = t), 900); }
        } catch { shareNow({}); }
      }, { passive: true });
    });
  };

  /* ─────────────────────────── Donate UX niceties ──────────────────────── */
  const focusDonate = () => {
    const cta = document.querySelector('[data-cta="donate"], .fc-hero-cta, a[href*="donate"]');
    if (!cta) return;
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          try { cta.setAttribute("tabindex", "0"); setTimeout(() => cta.focus({ preventScroll: true }), 250); } catch {}
          obs.disconnect();
        }
      });
    }, { rootMargin: "0px 0px -60% 0px", threshold: 0.4 });
    obs.observe(cta);
  };
  const donateHotkey = () => {
    addEventListener("keydown", (e) => {
      if ((e.key === "d" || e.key === "D") && !/input|textarea|select/i.test(e.target.tagName)) {
        const cta = document.querySelector('[data-cta="donate"], .fc-hero-cta, a[href*="donate"]');
        if (cta) { try { cta.click(); } catch {} }
      }
    }, { passive: true });
  };

  /* ─────────────────────────── Optional realtime (SSE) ─────────────────── */
  const bootSSE = () => {
    if ("io" in window) return; // socket.io present elsewhere
    const need = document.getElementById("donor-ticker") || document.getElementById("sponsor-leaderboard");
    if (!need) return;

    try {
      const es = new EventSource("/sse/donations");
      es.addEventListener("donation", (e) => {
        try {
          const data = JSON.parse(e.data);
          emit("fc:donation", data);
          const track = $("#donor-ticker .dt-track");
          if (track) {
            const item = document.createElement("span");
            item.className = "dt-item";
            const name = document.createElement("strong");
            name.textContent = data.name || "Anonymous";
            const amt = document.createElement("i");
            amt.textContent = data.amount ? ` — ${fmt.money(data.amount)}` : "";
            item.append(name, amt);
            track.prepend(item);
          }
        } catch {}
      });
      once("pagehide", () => { try { es.close(); } catch {} });
    } catch {}
  };

  /* ─────────────────────────── Lifecycle & telemetry ───────────────────── */
  const sendNet = () => emit("fc:network", { online: navigator.onLine });
  window.addEventListener("online", sendNet, { passive: true });
  window.addEventListener("offline", sendNet, { passive: true });
  once("DOMContentLoaded", sendNet);

  window.addEventListener("visibilitychange", () => emit("fc:visibility", { hidden: document.hidden }), { passive: true });
  window.addEventListener("pagehide", () => emit("fc:pagehide"), { passive: true });

  try {
    if ("PerformanceObserver" in window) {
      const po = new PerformanceObserver((list) => {
        for (const _ of list.getEntries()) {
          (window.dataLayer = window.dataLayer || []).push({ event: "fc_lcp_seen" });
          po.disconnect(); break;
        }
      });
      po.observe({ type: "largest-contentful-paint", buffered: true });
    }
  } catch {}

  /* ─────────────────────────── Error boundaries ────────────────────────── */
  let lastErrorTs = 0;
  const rateLimit = (ms) => { const now = Date.now(); if (now - lastErrorTs < ms) return false; lastErrorTs = now; return true; };
  window.addEventListener("error", (e) => {
    if (DEV) console.error("⛑️ Uncaught:", e.error || e.message);
    if (rateLimit(1500)) emit("fc:error", { type: "error", error: e.error || e.message });
  });
  window.addEventListener("unhandledrejection", (e) => {
    if (DEV) console.error("⛑️ Rejection:", e.reason);
    if (rateLimit(1500)) emit("fc:error", { type: "rejection", error: e.reason });
  });

  /* ─────────────────────────── Dynamic loaders ─────────────────────────── */
  const loadScript = (src, { type = "module", async = true, deferAttr = true, crossOrigin, integrity } = {}) =>
    new Promise((resolve, reject) => {
      const s = withNonce(document.createElement("script"));
      s.src = src; s.type = type;
      if (async) s.async = true;
      if (deferAttr) s.defer = true;
      if (crossOrigin) s.crossOrigin = crossOrigin;
      if (integrity) s.integrity = integrity;
      s.onload = () => resolve(); s.onerror = (e) => reject(e);
      document.head.appendChild(s);
    });
  const loadStyle = (href, { media = "all" } = {}) =>
    new Promise((resolve, reject) => {
      const l = withNonce(document.createElement("link"));
      l.rel = "stylesheet"; l.href = href; l.media = media;
      l.onload = () => resolve(); l.onerror = (e) => reject(e);
      document.head.appendChild(l);
    });

  Object.assign(window.fc, { loadScript, loadStyle, makeTrackedUrl });

  /* ─────────────────────────── App start ───────────────────────────────── */
  const start = async () => {
    const boot = (path, name) =>
      import(/* webpackChunkName: "[request]" */ path)
        .then((m) => (typeof m.default === "function" ? m.default() : undefined))
        .catch((err) => { if (DEV) console.warn(`↪️ ${name} skipped:`, err?.message || err); });

    await Promise.allSettled([
      boot("./site.js", "site.js"),
      boot("./sponsor.js", "sponsor.js"),
      boot("./fundraiser.js", "fundraiser.js"),
    ]);

    const needsPayments = !!(document.getElementById("sponsor-donation-form") ||
      document.getElementById("stripe-payment-element") ||
      document.getElementById("paypal-buttons"));
    if (needsPayments) {
      await import(/* webpackChunkName:"payments" */ "./payments.js").catch((err) => {
        if (DEV) console.warn("payments skipped:", err?.message || err);
      });
    }

    if (!("io" in window) && document.getElementById("sponsor-leaderboard")) {
      try { await import(/* webpackChunkName:"socketio" */ "./vendor/socketio.mjs"); }
      catch (err) { if (DEV) console.warn("socket.io wrapper not loaded:", err?.message || err); }
    }

    // Optional Alpine
    try {
      const { default: Alpine } = await import(/* webpackChunkName:"alpine" */ "alpinejs");
      window.Alpine = Alpine;
      Alpine.store?.("fc", { env: ENV, dev: DEV, csrf: csrfToken(), ref: refCtx });
      idle(() => Alpine.start());
    } catch (err) { if (DEV) console.warn("ℹ️ Alpine not present:", err?.message || err); }

    // Optional service worker (feature-flag via <html data-pwa>)
    idle(async () => {
      try {
        const ENABLE_PWA = html.hasAttribute("data-pwa") || /prod/i.test(ENV);
        if ("serviceWorker" in navigator && ENABLE_PWA) {
          const swUrl = "/static/js/elite-sw.js";
          const reg = await navigator.serviceWorker.register(swUrl, { scope: "/" });
          reg.update?.();
          emit("fc:sw:ready");
        }
      } catch (err) { if (DEV) console.warn("SW skipped:", err?.message || err); }
    });

    // P2P wiring after modules mount
    decorateDonations(document);
    hardenLinks(document);
    wireShares(document);
    window.fc.decorateLinks(document);
    focusDonate();
    donateHotkey();
    bootSSE();
    mo.observe(document.body, { subtree: true, childList: true });

    emit("fc:ready", { env: ENV, dev: DEV, prefs: prefers, ref: refCtx });
    if (bus) { try { bus.postMessage({ t: "fc:ready", env: ENV, ref: refCtx }); } catch {} }

    if (DEV) {
      const nav = performance.getEntriesByType?.("navigation")?.[0];
      console.warn("✅ app.entry booted", { env: ENV, serverTiming: nav?.serverTiming || [], refCtx });
    } else {
      console.warn("✅ app.entry.js loaded");
    }
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();

  /* ─────────────────────────── HMR (vite/webpack) ──────────────────────── */
  try { if (import.meta && import.meta.hot) { import.meta.hot.accept?.(); if (DEV) console.warn("🔁 HMR active"); } } catch {}
})();

