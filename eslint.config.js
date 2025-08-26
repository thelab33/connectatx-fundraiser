// eslint.config.js — FundChamps Prestige (fixed for ESLint 9+)

import js from "@eslint/js";
import globals from "globals";
import stylistic from "@stylistic/eslint-plugin";

export default [
  // Base recommended
  js.configs.recommended,

  {
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
    plugins: {
      "@stylistic": stylistic,
    },
    rules: {
      // Core
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
      "no-undef": "error",
      "eqeqeq": ["error", "smart"],
      "no-console": "off",

      // Stylistic
      "@stylistic/semi": ["error", "always"],
      "@stylistic/quotes": ["error", "double", { avoidEscape: true }],
      "@stylistic/indent": ["error", 2, { SwitchCase: 1 }],
      "@stylistic/no-trailing-spaces": "error",
      "@stylistic/comma-dangle": ["error", "only-multiline"],

      // Modern JS
      "prefer-const": "warn",
      "no-var": "error",
      "object-shorthand": ["error", "always"],
    },
  },

  // Special case: CommonJS files
  {
    files: ["**/*.cjs"],
    languageOptions: {
      sourceType: "script",
    },
  },

  // Frontend snippets (htmx/alpine scripts)
  {
    files: ["app/static/js/**/*.js"],
    rules: {
      "no-undef": "off",
    },
  },

  // Ignored paths (replaces .eslintignore)
  {
    ignores: [
      'app/static/js/main.js',
      'app/static/js/bundle.min.js',
      'app/static/js/**/vendor/**',
      'app/static/js/**/dist/**',
      'app/static/js/elite-sw.js',
      'app/static/js/elite-upgrades.js'
    ],
  },
];

