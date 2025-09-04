// eslint.config.mjs
import js from "@eslint/js";
import globals from "globals";
import importPlugin from "eslint-plugin-import";
import promise from "eslint-plugin-promise";
import unusedImports from "eslint-plugin-unused-imports";
import security from "eslint-plugin-security";
import eslintConfigPrettier from "eslint-config-prettier";

export default [
  // 0) Global ignores (keep CLI fast)
  {
    ignores: [
      "**/node_modules/**",
      "**/dist/**",
      "**/build/**",
      "**/.cache/**",
      "**/*.min.js",
      "app/static/js/vendor/**", // vendored bundles
      "migrations/**",
      ".venv/**",
      "venv/**",
    ],
  },

  // 1) Base JS recommended
  js.configs.recommended,

  // 2) App JS / ESM defaults (browser + node)
  {
    files: ["**/*.{js,mjs,cjs}"],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node,
        Alpine: "readonly",
        htmx: "readonly",
        io: "readonly",
        confetti: "readonly",
      },
    },
    plugins: {
      import: importPlugin,
      promise,
      "unused-imports": unusedImports,
      security,
    },
    settings: {
      "import/resolver": {
        node: { extensions: [".js", ".mjs", ".cjs"] },
      },
    },
    rules: {
      // Safer defaults
      "no-undef": "error",
      "no-var": "error",
      "prefer-const": "warn",
      eqeqeq: ["error", "smart"],

      // Console: allow warn/error; nudge on others
      "no-console": ["warn", { allow: ["warn", "error"] }],

      // Imports hygiene
      "import/order": [
        "warn",
        {
          groups: [
            "builtin",
            "external",
            "internal",
            ["parent", "sibling", "index"],
          ],
          "newlines-between": "always",
        },
      ],
      "import/no-mutable-exports": "error",

      // Unused imports/vars (plugin beats core rule)
      "no-unused-vars": "off",
      "unused-imports/no-unused-imports": "warn",
      "unused-imports/no-unused-vars": [
        "warn",
        {
          vars: "all",
          varsIgnorePattern: "^_",
          args: "after-used",
          argsIgnorePattern: "^_",
        },
      ],

      // Promises & basic security
      "promise/no-return-wrap": "error",
      "promise/always-return": "off",
      "promise/no-nesting": "warn",
      "security/detect-object-injection": "off", // too noisy for UI lists
    },
  },

  // 3) Config files: Node context, allow console
  {
    files: [
      "**/*.config.{js,mjs,cjs}",
      "eslint.config.mjs",
      "vite.config.*",
      "webpack.config.*",
      "tailwind.config.*",
    ],
    languageOptions: {
      globals: { ...globals.node },
      sourceType: "module",
    },
    rules: { "no-console": "off" },
  },

  // 4) Disable stylistic rules that conflict with Prettier (optional)
  eslintConfigPrettier,
];
