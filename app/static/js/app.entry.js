/**
 * app.entry.js — single entry that pulls in your libs + app code.
 * Output: app/static/js/bundle.min.js (via build.js)
 *
 * We import UMD/minified vendor files you already keep in /static/js/.
 * They set globals on window; we also defensively normalize a couple of helpers.
 */

// 1) Vendor libs you already have locally
import "./alpine.min.js";
import "./htmx.min.js";
import "./socket.io.js";
import "./confetti.js";

// 2) Your app modules (order matters if they expect globals)
import "./fc-header-hero.js";
import "./main.js"; // if you use a general site script; safe to keep

// 3) Expose/normalize globals (defensive)
(function () {
  // Alpine boot (if not auto-started)
  if (window.Alpine && !window.Alpine.version) {
    try {
      window.Alpine.start();
    } catch (_) {}
  }

  // htmx sane defaults
  if (window.htmx) {
    // Reduce noisy history cache, keep scroll behavior smooth
    window.htmx.config.historyCacheSize = 20;
    window.htmx.config.defaultSwapStyle = "outerHTML";
    // Optional: small progress indicator hook
    document.addEventListener("htmx:beforeRequest", () => window.showLoader?.());
    document.addEventListener("htmx:afterOnLoad", () => window.hideLoader?.());
    document.addEventListener("htmx:responseError", () => window.hideLoader?.());
  }

  // Socket.IO — ensure we have `window.io`
  if (typeof window.io !== "function") {
    console.warn("⚠️ socket.io client not detected at window.io");
  }

  // Confetti helper (map to your existing confetti global if present)
  if (!window.launchConfetti && typeof window.confetti === "function") {
    window.launchConfetti = (opts = {}) =>
      window.confetti(Object.assign({ particleCount: 120, spread: 70 }, opts));
  }

  // Dev hint
  if (process.env.NODE_ENV !== "production") {
    console.log("%cFundChamps dev mode", "color:#facc15;font-weight:bold");
  }
})();

