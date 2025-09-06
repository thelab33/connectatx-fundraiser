import './theme.js';            // Light/Dark auto-tuning + brand variable
import './micro.js';            // Micro-interactions (hover, ripple)
import './counters.js';         // Animated counters
import './ticker.js';           // Donor ticker marquee
import './badges.js';           // Milestone badges
import './stripe.js';           // Stripe seal helpers

// Auto-upgrade common elements by convention
document.addEventListener('DOMContentLoaded', () => {
  // 1) Tier CTAs
  document.querySelectorAll('[data-tier-cta]').forEach(el => el.classList.add('cta-pulse'));
  // 2) Hero & cards get glass + glow if opted-in
  document.querySelectorAll('[data-glass]').forEach(el => el.classList.add('glass2','ambient-glow'));
});

import './pro.js';


import './header.js';
