// postcss.config.mjs — FundChamps SaaS Prestige (ESM)
// Hardened, CSP-safe, production-aware PostCSS pipeline

import postcssImport from "postcss-import";
import tailwind from "tailwindcss";
import nested from "postcss-nested";
import autoprefixer from "autoprefixer";
import cssnano from "cssnano";
import safeParser from "postcss-safe-parser";

// If your CI/build system sets NODE_ENV, this will Just Work.
// (Vite/Next do this automatically for prod builds.)
const isProd = process.env.NODE_ENV === "production";

/** @type {import('postcss-load-config').Config} */
export default {
  // Safer parsing in production (prevents broken builds from malformed CSS)
  parser: isProd ? safeParser : undefined,

  // Source maps: bundlers typically control this, but leaving it on is harmless in dev.
  map: isProd ? false : { inline: true },

  plugins: [
    // 1) Resolve @imports (critical for modular CSS & tokens)
    postcssImport(),

    // 2) TailwindCSS with unified ESM config
    tailwind({ config: "./tailwind.config.mjs" }),

    // 3) Scoped nesting support (CSP-safe, avoids `&:is()` leaks)
    nested(),

    // 4) Autoprefix for wide browser support
    autoprefixer({
      flexbox: "no-2009",
      grid: "autoplace",
      overrideBrowserslist: [
        ">0.5%",
        "last 2 versions",
        "Firefox ESR",
        "not dead",
      ],
    }),

    // 5) Production-only optimizations
    ...(isProd
      ? [
          cssnano({
            preset: [
              "default",
              {
                discardComments: { removeAll: true },
                normalizeWhitespace: true,
                convertValues: { length: false }, // keep calc(0px) safe
                mergeLonghand: true,
                cssDeclarationSorter: true,
              },
            ],
          }),
        ]
      : []),
  ],
};

