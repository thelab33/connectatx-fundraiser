// eslint.config.js — FundChamps Prestige (ESLint 9+ Ready)

import js from "@eslint/js";
import globals from "globals";
import stylistic from "@stylistic/eslint-plugin";

export default [
  // ✅ Base recommended rules from ESLint
  js.configs.recommended,

  {
    // 🌐 Language + environment setup
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node,
        htmx: "readonly",
        Alpine: "readonly",
      },
    },

    // 🎨 Stylistic plugin for consistent code style
    plugins: {
      "@stylistic": stylistic,
    },

    // 🚦 Global ruleset
    rules: {
      // --- Core ---
      "no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "no-undef": "error",
      eqeqeq: ["error", "smart"],
      "no-console": "off", // Allow debug logs during dev

      // --- Style ---
      "@stylistic/semi": ["error", "always"],
      "@stylistic/quotes": ["error", "double", { avoidEscape: true }],
      "@stylistic/indent": ["error", 2, { SwitchCase: 1 }],
      "@stylistic/no-trailing-spaces": "error",
      "@stylistic/comma-dangle": ["error", "only-multiline"],

      // --- Modern JS ---
      "prefer-const": "warn",
      "no-var": "error",
      "object-shorthand": ["error", "always"],
    },
  },

  // 📦 CommonJS support (build scripts, configs, etc.)
  {
    files: ["**/*.cjs"],
    languageOptions: {
      sourceType: "script",
    },
  },

  // 🎭 Frontend micro-scripts (htmx, Alpine, inline widgets)
  {
    files: ["app/static/js/**/*.js"],
    rules: {
      "no-undef": "off", // ignore Alpine/htmx globals inside snippets
    },
  },

  // 🚫 Ignore heavy/minified/vendor builds
  {
    ignores: [
      "app/static/js/main.js",
      "app/static/js/bundle.min.js",
      "app/static/js/**/vendor/**",
      "app/static/js/**/dist/**",
      "app/static/js/elite-sw.js",
      "app/static/js/elite-upgrades.js",
    ],
  },
];
