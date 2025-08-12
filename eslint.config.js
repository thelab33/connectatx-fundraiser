// eslint.config.js
import js from "@eslint/js";
import globals from "globals";
import { defineConfig } from "eslint/config";

const VENDOR_IGNORES = [
  "app/static/js/*.min.js",
  "app/static/js/main.js",
];

export default defineConfig([
  { ignores: VENDOR_IGNORES },

  {
    files: ["app/static/js/**/*.js"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      ecmaVersion: "latest",
      sourceType: "module", // Switch to "script" if NOT using ESM
    },
    rules: {
      "no-console": "warn",
      "no-unused-vars": "warn",
    },
    // 🚩 **This next line is what actually applies the js recommended config!**
    ...js.configs.recommended,
  },
]);

