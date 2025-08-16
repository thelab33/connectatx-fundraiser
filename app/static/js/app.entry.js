// app/static/js/app.entry.js
// Main JS entry point for FundChamps / Connect ATX Elite

import "./site.js";           // your site-wide scripts
import "./fundraiser.js";     // fundraiser meter, real-time updates
import "./sponsor.js";        // sponsor interactions

// Optional: add polyfills or Alpine/HTMX here
import Alpine from "alpinejs";
window.Alpine = Alpine;
Alpine.start();

console.log("✅ app.entry.js loaded");

