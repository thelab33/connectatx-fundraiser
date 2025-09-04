/* eslint-disable no-empty */
/* app/static/js/starforge_enhancements.js */
/* Vanilla, CSP-safe, no dependencies. */
(() => {
  "use strict";
  if (window.__STARFORGE_READY__) return;
  window.__STARFORGE_READY__ = true;

  const $ = (s, ctx = document) => ctx.querySelector(s);
  void $;
  const $$ = (s, ctx = document) => Array.from(ctx.querySelectorAll(s));
  const clamp = (n, a, b) => Math.min(b, Math.max(a, n));

  /* 1) Reveal-on-scroll (cards, stats, rows) */
  const reveal = () => {
    if (!("IntersectionObserver" in window)) {
      $$(".reveal").forEach((el) => el.classList.add("is-in"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        for (const en of entries)
          if (en.isIntersecting) {
            en.target.classList.add("is-in");
            io.unobserve(en.target);
          }
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.12 },
    );
    $$(".reveal").forEach((el) => io.observe(el));
  };

  /* 2) Subtle hover lift on .card/.glass */
  const hoverLift = () => {
    const els = $$(".card, .glass");
    els.forEach((el) => {
      el.addEventListener(
        "mousemove",
        (e) => {
          const r = el.getBoundingClientRect();
          const dx = clamp((e.clientX - r.left) / r.width - 0.5, -1, 1);
          const dy = clamp((e.clientY - r.top) / r.height - 0.5, -1, 1);
          el.style.setProperty("--sf-tilt-x", (dy * -2).toFixed(3));
          el.style.setProperty("--sf-tilt-y", (dx * 2).toFixed(3));
          el.style.transform = `perspective(900px) rotateX(var(--sf-tilt-x,0deg)) rotateY(var(--sf-tilt-y,0deg)) translateY(-2px)`;
        },
        { passive: true },
      );
      el.addEventListener(
        "mouseleave",
        () => {
          el.style.transform = "";
        },
        { passive: true },
      );
    });
  };

  /* 3) CTA haptics (buttons feel “alive” without being flashy) */
  const ctaHaptics = () => {
    const ctas = $$(
      "[data-open-donate-modal], [data-analytics='cta:sponsor'], [data-analytics='cta:vip'], .btn, .sf-btn",
    );
    ctas.forEach((b) => {
      b.addEventListener(
        "pointerdown",
        () => {
          b.style.transform = "translateY(1px) scale(.995)";
        },
        { passive: true },
      );
      b.addEventListener(
        "pointerup",
        () => {
          b.style.transform = "";
        },
        { passive: true },
      );
    });
  };

  /* 4) Sticky Quick Donate visibility (only if header leaves viewport) */
  const quickDonate = () => {
    const floater = document.querySelector(
      '[data-analytics="cta:quick-donate"]',
    );
    const sentinel = document.getElementById("fc-header-sentinel");
    if (!floater || !sentinel || !("IntersectionObserver" in window)) return;
    const io = new IntersectionObserver(
      ([en]) => {
        floater.hidden = en.isIntersecting;
      },
      { threshold: 0 },
    );
    io.observe(sentinel);
  };

  /* 5) Safe copy-link buttons */
  const copyLinks = () => {
    $$("[data-copy-link]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const url = btn.getAttribute("data-copy-link") || location.href;
        try {
          await navigator.clipboard.writeText(url);
          btn.classList.add("copied");
          setTimeout(() => btn.classList.remove("copied"), 1600);
        } catch {}
      });
    });
  };

  /* 6) Auto-mark external links */
  const hardenExternal = () => {
    $$('a[target="_blank"]').forEach((a) => {
      if (!/noopener|noreferrer/.test(a.rel || ""))
        a.rel = (a.rel ? a.rel + " " : "") + "noopener noreferrer";
    });
  };

  /* 7) Auto lazyload/decoding for images without attrs (defensive) */
  const lazyImages = () => {
    $$("img:not([loading])").forEach((img) => (img.loading = "lazy"));
    $$("img:not([decoding])").forEach((img) => (img.decoding = "async"));
  };

  /* Kickoff when DOM is ready */
  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      () => {
        reveal();
        hoverLift();
        ctaHaptics();
        quickDonate();
        copyLinks();
        hardenExternal();
        lazyImages();
      },
      { once: true },
    );
  } else {
    reveal();
    hoverLift();
    ctaHaptics();
    quickDonate();
    copyLinks();
    hardenExternal();
    lazyImages();
  }
})();
setInterval(() => {
  document
    .querySelectorAll(".countdown-digit")
    .forEach((el) => el.classList.toggle("animate-pulse"));
}, 1000);
