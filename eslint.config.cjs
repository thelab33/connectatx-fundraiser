// eslint.config.js

import pkg from "eslint";
const { defineConfig } = pkg;

export default defineConfig({
  languageOptions: {
    globals: {
      io: "readonly",
      showDonationTicker: "readonly",
      htmx: "readonly",
      Alpine: "readonly",
    },
    parserOptions: {
      ecmaVersion: 12,
      sourceType: "module", // enables import/export
    },
  },
  ignorePatterns: [
    "app/static/js/*.min.js", // ignore vendor/minified scripts
    "node_modules/",
  ],
  extends: ["airbnb-base", "prettier"],
  plugins: ["import"],
  rules: {
    "no-unused-vars": "warn",
    "no-console": "off",
    "no-undef": "error",
    "no-prototype-builtins": "off",
  },
});
