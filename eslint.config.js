// eslint.config.js — FundChamps Prestige (Flat config, ESLint 9+)

import js from "@eslint/js";
import globals from "globals";
import stylistic from "@stylistic/eslint-plugin";
import importPlugin from "eslint-plugin-import";
import compat from "eslint-plugin-compat";
import unusedImports from "eslint-plugin-unused-imports";
// (Optional) lightweight security checks; keep noisy rule off by default.
// import security from "eslint-plugin-security";

const browserGlobals = {
  ...globals.browser,
  htmx: "readonly",
  Alpine: "readonly",
  dataLayer: "readonly",
  posthog: "readonly",
  FC: "readonly",
};

const nodeGlobals = { ...globals.node };

export default [
  // Base recommended
  js.configs.recommended,

  // ---------- Global defaults (ES modules in modern browsers) ----------
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: browserGlobals,
    },
    plugins: {
      "@stylistic": stylistic,
      import: importPlugin,
      compat,
      "unused-imports": unusedImports,
      // security,
    },
    settings: {
      // Let compat read your browserslist from package.json
      // (alternatively: { targets: [ "defaults", "not IE 11", ... ] })
      // Keep empty: compat will auto-resolve from browserslist.
    },
    rules: {
      /* Core */
      "no-undef": "error",
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
      "no-empty": ["error", { allowEmptyCatch: true }],
      eqeqeq: ["error", "smart"],
      "no-var": "error",
      "prefer-const": "warn",
      "object-shorthand": ["error", "always"],
      "no-console": "off", // okay in app code; tighten in build scripts below

      /* Import hygiene */
      "import/first": "error",
      "import/no-duplicates": "error",
      "import/no-mutable-exports": "error",
      "import/order": [
        "warn",
        {
          groups: [["builtin", "external"], ["internal"], ["parent", "sibling", "index"]],
          "newlines-between": "always",
          alphabetize: { order: "asc", caseInsensitive: true },
        },
      ],

      /* Dead code cleanup */
      "unused-imports/no-unused-imports": "warn",
      "unused-imports/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_", caughtErrorsIgnorePattern: "^_" },
      ],

      /* Browser compat (uses your browserslist) */
      "compat/compat": "warn",

      /* Style */
      "@stylistic/semi": ["error", "always"],
      "@stylistic/quotes": ["error", "double", { avoidEscape: true }],
      "@stylistic/indent": ["error", 2, { SwitchCase: 1 }],
      "@stylistic/no-trailing-spaces": "error",
      "@stylistic/comma-dangle": ["error", "only-multiline"],

      /* (Optional) Security — enable if you want stricter checks
      "security/detect-object-injection": "off",
      */
    },
  },

  // ---------- Node / build scripts / config files ----------
  {
    files: [
      "**/*.cjs",
      "build.js",
      "scripts/**/*.mjs",
      "scripts/**/*.js",
      "*.config.cjs",
      "*.config.js",
      "tailwind.config.cjs",
      "stylelint.config.cjs",
      "postcss.config.cjs",
      "eslint.config.js",
    ],
    languageOptions: {
      sourceType: "script",
      globals: nodeGlobals,
    },
    rules: {
      // Stricter in build scripts
      "no-console": ["warn", { allow: ["info", "warn", "error"] }],
      // Node import style is looser
      "import/no-extraneous-dependencies": "off",
      "import/order": "off",
      "compat/compat": "off",
    },
  },

  // ---------- Service Worker / Web Worker (if you add one later) ----------
  {
    files: ["app/static/js/**/sw*.js", "app/static/js/**/worker*.js"],
    languageOptions: {
      globals: {
        ...browserGlobals,
        ServiceWorkerGlobalScope: "readonly",
        self: "readonly",
      },
    },
    rules: {
      "no-restricted-globals": "off",
    },
  },

  // ---------- Frontend micro-scripts in templates bundle ----------
  {
    files: ["app/static/js/**/*.js"],
    rules: {
      // Inline widget globals are common; keep relaxed
      "no-undef": "off",
    },
  },

  // ---------- Ignore built files & vendor blobs ----------
  {
    ignores: [
      "node_modules/**",
      "dist/**",
      ".cache/**",
      "app/static/js/main.js",
      "app/static/js/bundle.min.js",
      "app/static/js/**/vendor/**",
      "app/static/js/**/dist/**",
      "app/static/js/elite-sw.js",
      "app/static/js/elite-upgrades.js",
    ],
  },
];

