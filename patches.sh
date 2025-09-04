#!/usr/bin/env bash
# =========================================================
# FC HERO PATCH — Hologram polish, vertical pill styling,
# and raised hero bar placement.
# Run once: ./patches.sh
# =========================================================

CSS_FILE="app/static/css/fc_elite.css"

cat <<'EOF' >> $CSS_FILE

/* =========================================================
   HERO PATCH: Hologram, Pill, and Hero Bar
   ========================================================= */

/* --- 3D Hero Card Polish --- */
#fc-hero .fc-hero-card {
  transform-style: preserve-3d;
  perspective: 1600px;
}
#fc-hero .fc-hero-card__frame {
  transition: transform .4s ease, box-shadow .4s ease;
}
#fc-hero .fc-hero-card:hover .fc-hero-card__frame {
  transform: translateZ(60px) rotateX(2deg) rotateY(-2deg);
  box-shadow: 0 24px 80px rgba(0,0,0,.55), inset 0 0 12px rgba(255,255,255,.12);
}
#fc-hero .fc-hero-card__glare {
  animation: heroGlareMove 6s linear infinite;
}
@keyframes heroGlareMove {
  0%   { background-position: 0% 50%; opacity:.25 }
  50%  { background-position: 100% 50%; opacity:.6 }
  100% { background-position: 0% 50%; opacity:.25 }
}

/* --- Hologram Headline Boost --- */
#fc-hero .holo3d {
  filter: drop-shadow(0 0 20px rgba(250,204,21,.45));
}
#fc-hero[data-holo-boost="1"] .holo3d {
  filter: drop-shadow(0 0 25px rgba(64,240,255,.5)) drop-shadow(0 0 14px rgba(250,204,21,.4));
}

/* --- Vertical Team Pill (rail/spine) --- */
#fc-hero .fc-hero-spine {
  border:1px solid rgba(255,255,255,.25);
  background:linear-gradient(180deg,rgba(255,255,255,.12),rgba(255,255,255,.03));
  backdrop-filter: blur(8px) saturate(140%);
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.25),
              0 0 20px color-mix(in srgb, var(--accent) 35%, transparent);
}
#fc-hero .fc-hero-spine .spine-text {
  font-weight:900;
  letter-spacing:.2em;
  color:color-mix(in srgb, var(--accent) 70%, #fff 30%);
  text-shadow:0 0 6px rgba(0,0,0,.55);
  mix-blend-mode:overlay;
}

/* --- Hero Overlay + Bar Adjustment --- */
#fc-hero .fc-hero-overlay {
  padding-bottom: 2.5rem; /* lift text higher */
}
#fc-hero .fc-hero-bar {
  margin-top: .8rem; /* extra space below headline */
}
#fc-hero .hero-meter {
  margin-top: .4rem;
}

EOF

echo "✅ Hero polish patch applied to $CSS_FILE"

