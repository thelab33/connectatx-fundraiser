(() => {
  "use strict";

  // ——— utilities ———
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const on = (el, ev, fn) => el && el.addEventListener(ev, fn, { passive: true });

  // Dispatch a single analytics hook for all tracked clicks
  on(document, "click", (e) => {
    const t = e.target.closest("[data-track]");
    if (!t) return;
    const detail = { action: t.dataset.track, href: t.getAttribute("href") || null };
    window.dispatchEvent(new CustomEvent("fc:track", { detail }));
  });

  // ——— mobile menu (replaces Alpine) ———
  const mobileMenu = $("#mobile-menu");
  const burger = document.querySelector('button[aria-controls="mobile-menu"]');
  if (burger && mobileMenu) {
    const closeMenu = () => {
      mobileMenu.setAttribute("hidden", "true");
      burger.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
    };
    const openMenu = () => {
      mobileMenu.removeAttribute("hidden");
      burger.setAttribute("aria-expanded", "true");
      document.body.style.overflow = "hidden";
    };
    on(burger, "click", () => (burger.getAttribute("aria-expanded") === "true" ? closeMenu() : openMenu()));
    on(document, "keydown", (e) => e.key === "Escape" && closeMenu());
    // Close on menu click
    $$("#mobile-menu a").forEach((a) => on(a, "click", closeMenu));
    // Start hidden for CSP/no-FOUC
    mobileMenu.setAttribute("hidden", "true");
  }

  // ——— announcement bar (persist dismissal) ———
  const ANNOUNCEMENT_KEY = "fc:announce:dismissed";
  const bar = $("#announcement-bar");
  if (bar) {
    if (localStorage.getItem(ANNOUNCEMENT_KEY) === "1") {
      bar.remove();
    } else {
      const btn = bar.querySelector("button[aria-label='Close announcement']");
      on(btn, "click", () => {
        localStorage.setItem(ANNOUNCEMENT_KEY, "1");
        bar.remove();
      });
    }
  }

  // ——— countdown ———
  const countdownEl = $("#header-countdown");
  if (countdownEl) {
    const iso = countdownEl.dataset.deadline;
    let target = iso ? new Date(iso) : null;
    if (!target || isNaN(+target)) {
      countdownEl.textContent = "";
    } else {
      const tick = () => {
        const diff = +target - Date.now();
        if (diff <= 0) {
          countdownEl.textContent = "Final hours!";
          countdownEl.closest("[role='region']")?.classList.add("expired");
          clearInterval(iv);
          return;
        }
        const s = Math.floor(diff / 1000);
        const d = Math.floor(s / 86400);
        const h = Math.floor((s % 86400) / 3600);
        const m = Math.floor((s % 3600) / 60);
        countdownEl.textContent = `${d}d ${h}h ${m}m`;
      };
      tick();
      const iv = setInterval(tick, 30_000);
    }
  }

  // ——— image fallback ———
  $$("img[data-fallback]").forEach((img) => {
    on(img, "error", () => {
      const fb = img.getAttribute("data-fallback");
      if (fb && img.src !== fb) img.src = fb;
    });
  });

  // ——— modal: open/close/focus trap ———
  const openers = $$("[data-modal-open]");
  const closers = $$("[data-modal-close]");
  const modals = $$("dialog[id]");
  const lastFocus = new WeakMap();

  function trapFocus(modal) {
    const focusables = modal.querySelectorAll(
      'a,button,input,select,textarea,[tabindex]:not([tabindex="-1"])'
    );
    if (!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    on(modal, "keydown", (e) => {
      if (e.key !== "Tab") return;
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus();
      }
    });
  }

  function openModal(id, openerEl) {
    const modal = document.getElementById(id);
    if (!modal) return;
    lastFocus.set(modal, openerEl || document.activeElement);
    if (typeof modal.showModal === "function") modal.showModal();
    else modal.setAttribute("open", "true");
    trapFocus(modal);
    const toFocus = modal.querySelector("[autofocus]") || modal.querySelector("h2,button,video");
    toFocus?.focus();
  }

  function closeModal(modal) {
    if (!modal) return;
    if (typeof modal.close === "function") modal.close();
    else modal.removeAttribute("open");
    (lastFocus.get(modal) || $("[data-modal-open]"))?.focus?.();
  }

  openers.forEach((btn) =>
    on(btn, "click", () => openModal(btn.getAttribute("data-modal-open"), btn))
  );
  closers.forEach((btn) =>
    on(btn, "click", () => closeModal(btn.closest("dialog")))
  );
  modals.forEach((m) => {
    on(m, "click", (e) => e.target === m && closeModal(m)); // click-backdrop
    on(document, "keydown", (e) => e.key === "Escape" && m.hasAttribute("open") && closeModal(m));
  });

  // ——— animated live ticker (gentle count up) ———
  const ticker = $("#live-ticker");
  if (ticker) {
    const initial = parseFloat((ticker.dataset.initial || "0").replace(/[^0-9.]/g, "")) || 0;
    let current = initial;
    const render = () => (ticker.textContent = `💰 $${Math.round(current).toLocaleString()}`);
    render();
    window.addEventListener("fc:updateRaised", (e) => {
      const target = Number(e.detail?.amount || 0);
      const delta = Math.max(0, target - current);
      if (!delta) return;
      const steps = 24, per = delta / steps;
      let i = 0;
      const iv = setInterval(() => {
        current += per; i++; render();
        if (i >= steps) { current = target; render(); clearInterval(iv); }
      }, 30);
    });
  }

})();

