module.exports = {
  env: { browser: true, es2022: true },
  extends: ["eslint:recommended", "plugin:compat/recommended"],
  plugins: ["compat", "security", "unused-imports"],
  rules: {
    "no-unused-vars": "off",
    "unused-imports/no-unused-vars": [
      "error",
      { args: "none", ignoreRestSiblings: true },
    ],
    "no-implicit-globals": "error",
    "no-console": ["warn", { allow: ["warn", "error"] }],
  },
  globals: { Stripe: "readonly", paypal: "readonly" },
};
