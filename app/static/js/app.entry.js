/* eslint-disable no-empty */
// app/static/js/app.entry.js
// FundChamps / Connect ATX Elite
// CSP-safe, production-ready entry

(() => {
  'use strict';
  if (window.__FC_APP_INIT__) return;
  window.__FC_APP_INIT__ = true;

  /* ---------- Env / flags ---------- */
  const html = document.documentElement;
  html.classList.add('js'); html.classList.remove('no-js');
  html.setAttribute('data-fc-app', 'true');

  const ENV = html.getAttribute('data-env') || window.APP_ENV || 'production';
  const DEV = /dev|local/.test(String(ENV).toLowerCase());
  const mql = (q) => !!(window.matchMedia && window.matchMedia(q).matches);
  const prefers = {
    reducedMotion: mql('(prefers-reduced-motion: reduce)'),
    reducedData: !!(navigator.connection && (navigator.connection.saveData || String(navigator.connection.effectiveType||'').includes('2g'))),
    highContrast: mql('(prefers-contrast: more)'),
  };
  if (prefers.reducedMotion || prefers.reducedData) html.classList.add('fc-reduced');

  /* ---------- DOM helpers ---------- */
  const $  = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const once = (type, fn, opts) => {
    const wrapped = (e) => { try { fn(e); } finally { window.removeEventListener(type, wrapped, opts); } };
    window.addEventListener(type, wrapped, opts);
  };

  /* ---------- CSP nonce discovery (meta or current script) ---------- */
  let NONCE = $('meta[name="csp-nonce"]')?.content || '';
  if (!NONCE) { try { NONCE = document.currentScript?.nonce || ''; } catch {} }
  const withNonce = (el) => { if (NONCE) el.setAttribute('nonce', NONCE); return el; };

  /* ---------- Cookies / CSRF ---------- */
  const getCookie = (k) => {
    try {
      const m = document.cookie.match(new RegExp('(^|;\\s*)' + k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '=([^;]*)'));
      return m ? decodeURIComponent(m[2]) : '';
    } catch { return ''; }
  };
  const csrfToken = () => $('meta[name="csrf-token"]')?.content || getCookie('csrf_token') || '';

  /* ---------- Broadcast channel (optional) ---------- */
  let bus = null; try { bus = new BroadcastChannel('fc_ui'); } catch {}
  const emit = (type, detail) => window.dispatchEvent(new CustomEvent(type, { detail }));
  const on   = (type, fn, opts) => { window.addEventListener(type, fn, opts); return () => window.removeEventListener(type, fn, opts); };

  /* ---------- Same-origin check ---------- */
  const isSameOrigin = (input) => {
    try {
      const u =
        typeof input === 'string' ? new URL(input, location.href)
        : input instanceof Request ? new URL(input.url, location.href)
        : input?.url ? new URL(input.url, location.href)
        : null;
      return !u || u.origin === location.origin;
    } catch { return false; }
  };

  /* ---------- Perf helpers ---------- */
  const idle = (fn, timeout = 1200) =>
    ('requestIdleCallback' in window)
      ? window.requestIdleCallback(fn, { timeout })
      : setTimeout(fn, 0);
  const raf   = (fn) => requestAnimationFrame(fn);
  const defer = (fn) => idle(() => raf(fn));

  /* ---------- Dynamic loaders (CSP-safe) ---------- */
  const loadScript = (src, { type = 'module', async = true, deferAttr = true, crossOrigin, integrity } = {}) =>
    new Promise((resolve, reject) => {
      const s = withNonce(document.createElement('script'));
      s.src = src; s.type = type; if (async) s.async = true; if (deferAttr) s.defer = true;
      if (crossOrigin) s.crossOrigin = crossOrigin;
      if (integrity)  s.integrity  = integrity;
      s.onload = () => resolve(); s.onerror = (e) => reject(e);
      document.head.appendChild(s);
    });

  const loadStyle = (href, { media = 'all' } = {}) =>
    new Promise((resolve, reject) => {
      const l = withNonce(document.createElement('link'));
      l.rel = 'stylesheet'; l.href = href; l.media = media;
      l.onload = () => resolve(); l.onerror = (e) => reject(e);
      document.head.appendChild(l);
    });

  /* ---------- fetch hardening + helpers ---------- */
  const _fetch = window.fetch ? window.fetch.bind(window) : null;

  const withTimeout = (ms, upstream) => {
    const local = new AbortController();
    const id = setTimeout(() => local.abort(new DOMException('Timeout', 'AbortError')), ms);
    upstream?.addEventListener?.('abort', () => { try { clearTimeout(id); local.abort(upstream.reason); } catch {} }, { once:true });
    return { signal: local.signal, cancel: () => clearTimeout(id) };
  };

  // Hardened fetch: credentials same-origin + headers + timeout + (optional) retry for idempotent same-origin
  async function fetchSafe(input, init = {}, { timeout = 12000, retries = 0 } = {}) {
    if (!_fetch) throw new Error('fetch not available');
    const method  = String(init.method || 'GET').toUpperCase();
    const same    = isSameOrigin(input);
    const headers = new Headers(init.headers || {});
    if (!headers.has('Accept')) headers.set('Accept','application/json, text/html;q=0.9, */*;q=0.8');
    if (same && !headers.has('X-Requested-With')) headers.set('X-Requested-With','XMLHttpRequest');
    const mutating = !['GET','HEAD','OPTIONS','TRACE'].includes(method);
    if (same && mutating && !headers.has('X-CSRFToken')) {
      const tok = csrfToken(); if (tok) headers.set('X-CSRFToken', tok);
    }

    const upstream = init.signal;
    const { signal, cancel } = withTimeout(timeout, upstream);

    let attempt = 0;
    // eslint-disable-next-line no-constant-condition
    while (true) {
      try {
        const res = await _fetch(input, { credentials:'same-origin', ...init, headers, signal });
        cancel();
        return res;
      } catch (err) {
        const retriable = !mutating && same &&
          (err?.name === 'AbortError' || /NetworkError|load failed|Failed to fetch/i.test(String(err?.message||'')));
        if (!(retriable && attempt < retries)) throw err;
        await new Promise(r => setTimeout(r, 300 * Math.pow(2, attempt++))); // 300ms, 600ms, 1200ms...
      }
    }
  }

  async function fetchJSON(input, init = {}, opts = {}) {
    const res = await fetchSafe(input, init, opts);
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      const err = new Error(`HTTP ${res.status} ${res.statusText}`); err.status = res.status; err.body = text; throw err;
    }
    if (res.status === 204) return null;
    const ct = res.headers.get('content-type') || '';
    return ct.includes('application/json') ? res.json() : res.text();
  }

  async function postJSON(url, data, init = {}, opts = {}) {
    const body = data instanceof FormData ? data : JSON.stringify(data ?? {});
    const headers = new Headers(init.headers || {});
    if (!(data instanceof FormData) && !headers.has('Content-Type')) headers.set('Content-Type','application/json');
    return fetchJSON(url, { method:'POST', body, headers, ...init }, opts);
  }

  // Public FC namespace
  window.fc = Object.assign(window.fc || {}, {
    env: ENV, dev: DEV, prefs: prefers, bus, csrf: csrfToken,
    on, emit, $, $$, idle, raf, defer, loadScript, loadStyle,
    fetchJSON, postJSON, fetchSafe,
  });

  /* ---------- Patch global fetch (non-breaking) ---------- */
  if (_fetch) {
    window.fetch = (input, init = {}) => fetchSafe(input, init);
  }

  /* ---------- HTMX hardening (optional) ---------- */
  if (window.htmx) {
    try {
      window.htmx.config.withCredentials = true;
      window.htmx.config.scrollBehavior = 'instant';
      document.body.addEventListener('htmx:configRequest', (e) => {
        if (isSameOrigin(e.detail.path)) {
          e.detail.headers['X-Requested-With'] = 'XMLHttpRequest';
          const tok = csrfToken(); if (tok) e.detail.headers['X-CSRFToken'] = tok;
        }
      });
    } catch {}
  }

  /* ---------- Network + page lifecycle signals ---------- */
  const sendNet = () => emit('fc:network', { online: navigator.onLine });
  window.addEventListener('online',  sendNet, { passive:true });
  window.addEventListener('offline', sendNet, { passive:true });
  once('DOMContentLoaded', sendNet);

  window.addEventListener('visibilitychange', () => emit('fc:visibility', { hidden: document.hidden }), { passive:true });
  window.addEventListener('pagehide', () => emit('fc:pagehide'), { passive:true });

  /* ---------- Error boundaries (rate-limited) ---------- */
  let lastErrorTs = 0;
  const rateLimit = (ms) => { const now = Date.now(); if (now - lastErrorTs < ms) return false; lastErrorTs = now; return true; };
  window.addEventListener('error', (e) => {
    if (DEV) console.error('⛑️ Uncaught:', e.error || e.message);
    if (rateLimit(1500)) emit('fc:error', { type:'error', error: e.error || e.message });
  });
  window.addEventListener('unhandledrejection', (e) => {
    if (DEV) console.error('⛑️ Rejection:', e.reason);
    if (rateLimit(1500)) emit('fc:error', { type:'rejection', error: e.reason });
  });

  /* ---------- App start ---------- */
  const start = async () => {
    const boot = (path, name) =>
      import(/* webpackChunkName: "[request]" */ path)
        .then((m) => (typeof m.default === 'function' ? m.default() : undefined))
        .catch((err) => { if (DEV) console.warn(`↪️ ${name} skipped:`, err?.message || err); });

    // Stage feature modules (site → sponsor → fundraiser)
    await Promise.allSettled([
      boot('./site.js', 'site.js'),
      boot('./sponsor.js', 'sponsor.js'),
      boot('./fundraiser.js', 'fundraiser.js'),
    ]);

    // Lazy-load payments only if donation UI exists
    const needsPayments = !!(
      document.getElementById('sponsor-donation-form') ||
      document.getElementById('stripe-payment-element') ||
      document.getElementById('paypal-buttons')
    );
    if (needsPayments) {
      await import(/* webpackChunkName:"payments" */ './payments.js')
        .catch(err => { if (DEV) console.warn('payments skipped:', err?.message || err); });
    }

    // Lazy-load Socket.IO wrapper if leaderboard present and no global io yet
    if (!('io' in window) && document.getElementById('sponsor-leaderboard')) {
      try {
        await import(/* webpackChunkName:"socketio" */ './vendor/socketio.mjs');
      } catch (err) {
        if (DEV) console.warn('socket.io wrapper not loaded:', err?.message || err);
      }
    }

    // Optional Alpine
    try {
      const { default: Alpine } = await import(/* webpackChunkName:"alpine" */ 'alpinejs');
      window.Alpine = Alpine;
      Alpine.store?.('fc', { env: ENV, dev: DEV, csrf: csrfToken() });
      idle(() => Alpine.start());
    } catch (err) { if (DEV) console.warn('ℹ️ Alpine not present:', err?.message || err); }

    // Optional service worker (feature-flag via <html data-pwa>)
    idle(async () => {
      try {
        const ENABLE_PWA = html.hasAttribute('data-pwa') || /prod/i.test(ENV);
        if ('serviceWorker' in navigator && ENABLE_PWA) {
          // Use your file if you keep it; fallback to /sw.js if you relocate later
          const swUrl = '/static/js/elite-sw.js';
          await navigator.serviceWorker.register(swUrl, { scope: '/' });
          emit('fc:sw:ready');
        }
      } catch (err) { if (DEV) console.warn('SW skipped:', err?.message || err); }
    });

    emit('fc:ready', { env: ENV, dev: DEV, prefs: prefers });
    if (bus) { try { bus.postMessage({ t: 'fc:ready', env: ENV }); } catch {} }

    if (DEV) {
      const nav = performance.getEntriesByType?.('navigation')?.[0];
      console.warn('✅ app.entry booted', { env: ENV, serverTiming: nav?.serverTiming || [] });
    } else {
      // single-line for log sampling in prod
      console.warn('✅ app.entry.js loaded');
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }

  /* ---------- HMR (vite/webpack) ---------- */
  try {
    if (import.meta && import.meta.hot) {
      import.meta.hot.accept?.();
      if (DEV) console.warn('🔁 HMR active');
    }
  } catch {}
})();

