// postcss.config.cjs — FundChamps SaaS Prestige (Critical Split)
// CSP-safe • Tailwind-aware • Critical-First loading for 🚀 LCP

const isProd = process.env.NODE_ENV === "production";
const purgecss = require("@fullhuman/postcss-purgecss");

module.exports = {
  plugins: {
    // ---------------- Core ----------------
    tailwindcss: { config: "./tailwind.config.cjs" },
    autoprefixer: {
      flexbox: "no-2009",
      grid: "autoplace",
    },

    // ---------------- Hardening ----------------
    "postcss-safe-parser": {},
    "postcss-normalize": isProd ? {} : false,

    // ---------------- Production Only ----------------
    ...(isProd
      ? {
          // Purge unused utilities, keeping only what’s in your Jinja/JS/Py
          "@fullhuman/postcss-purgecss": purgecss({
            content: [
              "./app/templates/**/*.{html,jinja,jinja2}",
              "./app/templates/partials/**/*.{html,jinja,jinja2}",
              "./app/templates/macros/**/*.{html,jinja,jinja2}",
              "./app/**/*.py",
              "./app/static/js/**/*.{js,ts,mjs}",
            ],
            defaultExtractor: (content) =>
              content.match(/[\w-/:.%]+(?<!:)/g) || [],
            safelist: [
              // keep your prestige safelist in tailwind.config.cjs
              // you can also pull dynamic classes in here
              "dark",
              "glass-card",
              "focus-ring-brand",
              /backdrop-blur-.+/,
            ],
          }),

          // Compress + dedupe CSS
          cssnano: {
            preset: [
              "default",
              {
                discardComments: { removeAll: true },
                normalizeWhitespace: true,
                colormin: true,
                convertValues: { length: false },
              },
            ],
          },
          "postcss-discard-duplicates": {},
        }
      : {}),
  },
};
