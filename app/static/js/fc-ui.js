// app/static/js/fc-ui.js — Alpine + HTMX helpers (ESM, CSP-safe)
const clamp = (n, min, max) => Math.min(max, Math.max(min, n));
const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

// --- HERO TILT ---------------------------------------------------
export function heroTilt() {
  return {
    tiltMax: 7,          // deg
    card: null,
    raf: 0,
    rect: null,
    init() {
      this.card = this.$refs.card || this.$el.querySelector(".fc-hero-card");
      if (!this.card) return;
      const onEnter = () => (this.rect = this.card.getBoundingClientRect());
      const onLeave = () => {
        cancelAnimationFrame(this.raf);
        this.card.style.transform = "translateZ(0) rotateX(0) rotateY(0)";
      };
      const onMove = (e) => {
        if (!this.rect) this.rect = this.card.getBoundingClientRect();
        const x = (e.clientX - this.rect.left) / this.rect.width;
        const y = (e.clientY - this.rect.top) / this.rect.height;
        const mx = clamp(x * 100, 0, 100);
        const my = clamp(y * 100, 0, 100);
        const ry = (x - 0.5) * this.tiltMax * 2;
        const rx = (0.5 - y) * this.tiltMax * 2;
        this.$el.style.setProperty("--mx", `${mx}%`);
        this.$el.style.setProperty("--my", `${my}%`);
        cancelAnimationFrame(this.raf);
        this.raf = requestAnimationFrame(() => {
          this.card.style.transform = `translateZ(0) rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg)`;
        });
      };
      this.$el.addEventListener("pointerenter", onEnter);
      this.$el.addEventListener("pointermove", onMove);
      this.$el.addEventListener("pointerleave", onLeave);
    },
  };
}

// --- MINI RAIL ---------------------------------------------------
export function miniRail() {
  return {
    progress: 0,
    _tick: null,
    init() {
      const calc = () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop || 0;
        const doc = document.documentElement;
        const h = doc.scrollHeight - doc.clientHeight;
        this.progress = clamp((h > 0 ? (scrollTop / h) * 100 : 0), 0, 100);
        this.$el.style.setProperty("--w", `${this.progress}%`);
      };
      const onScroll = () => {
        if (this._tick) return;
        this._tick = requestAnimationFrame(() => {
          this._tick = null;
          calc();
        });
      };
      calc();
      window.addEventListener("scroll", onScroll, { passive: true });
      window.addEventListener("resize", onScroll);
    },
  };
}

// --- METER (viewport + HTMX aware) -------------------------------
export function meter(opts = {}) {
  return {
    value: Number(opts.value ?? this.$el.dataset.progress ?? this.$el.getAttribute("aria-valuenow") ?? 0),
    animated: opts.animated ?? true,
    duration: Number(opts.duration ?? 800),
    _bar: null,
    _io: null,
    _animId: 0,
    init() {
      this._bar = this.$el.querySelector(".fc-meter__bar, .bar");
      if (!this._bar) return;
      this._apply(this.value, false);
      // Animate when visible
      this._io = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            this.animateTo(this._readAttr());
            this._io.disconnect();
          }
        });
      }, { threshold: 0.25 });
      this._io.observe(this.$el);
    },
    _readAttr() {
      const raw = this.$el.dataset.progress ?? this.$el.getAttribute("aria-valuenow") ?? this.value;
      let v = Number(raw);
      // Accept 0–1 or 0–100; normalize to 0–1
      if (v > 1) v = v / 100;
      return clamp(v, 0, 1);
    },
    _apply(v, withTransition = true) {
      if (!withTransition) this._bar.style.transition = "none";
      this.$el.style.setProperty("--p", v);
      // force reflow to re-enable transition next frame
      if (!withTransition) requestAnimationFrame(() => (this._bar.style.transition = ""));
    },
    animateTo(target) {
      cancelAnimationFrame(this._animId);
      const start = performance.now();
      const from = Number(getComputedStyle(this.$el).getPropertyValue("--p")) || 0;
      const run = (t) => {
        const dt = clamp((t - start) / this.duration, 0, 1);
        const eased = from + (target - from) * easeOutCubic(dt);
        this._apply(eased, true);
        if (dt < 1) this._animId = requestAnimationFrame(run);
      };
      this._animId = requestAnimationFrame(run);
    },
    // Public API for HTMX/updates
    set(v) {
      const norm = v > 1 ? v / 100 : v;
      this.$el.dataset.progress = String(norm);
      this.animateTo(clamp(norm, 0, 1));
    },
  };
}

// --- HTMX glue (optional but handy) -------------------------------
export function bindHtmx() {
  if (!window.htmx) return;
  const refreshMeters = (root = document) => {
    root.querySelectorAll(".fc-meter,[x-data*=meter]").forEach((el) => {
      const api = el.__x ? el.__x.$data : null; // Alpine component instance (if present)
      const raw = el.dataset.progress ?? el.getAttribute("aria-valuenow");
      if (raw != null) {
        const v = Number(raw);
        if (api && typeof api.set === "function") api.set(v);
        else {
          // vanilla fallback
          const bar = el.querySelector(".fc-meter__bar, .bar");
          if (bar) el.style.setProperty("--p", v > 1 ? v / 100 : v);
        }
      }
    });
  };
  document.addEventListener("htmx:afterSwap", (e) => refreshMeters(e.target));
  document.addEventListener("htmx:afterSettle", (e) => refreshMeters(e.target));
}

// --- Bootstrap (register Alpine components when available) -------
export function registerAlpine() {
  if (!window.Alpine) return;
  window.Alpine.data("heroTilt", heroTilt);
  window.Alpine.data("miniRail", miniRail);
  window.Alpine.data("meter", meter);
}

// Auto-wire after DOM ready
document.addEventListener("alpine:init", () => {
  registerAlpine();
  bindHtmx();
});

// Also attempt to bind if Alpine was loaded before this file
if (window.Alpine) {
  registerAlpine();
  bindHtmx();
}

