// postcss.config.cjs — FundChamps SaaS Prestige
const isProd = process.env.NODE_ENV === "production";
const purgecss = require("@fullhuman/postcss-purgecss");

module.exports = {
  plugins: {
    // ---------------- Core ----------------
    tailwindcss: { config: "./tailwind.config.mjs" },
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
          "@fullhuman/postcss-purgecss": purgecss({
            content: [
              "./app/templates/**/*.{html,jinja,jinja2}",
              "./app/**/*.py",
              "./app/static/js/**/*.{js,ts,mjs}",
            ],
            defaultExtractor: (content) =>
              content.match(/[\w-/:.%]+(?<!:)/g) || [],
            safelist: [
              "dark",
              "glass-card",
              "focus-ring-brand",
              /backdrop-blur-.+/,
            ],
          }),
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

