module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true, // Support Node globals (like module)
    amd: true, // Support AMD (like define)
  },
  globals: {
    module: "readonly",
    define: "readonly",
    io: "readonly", // for socket.io usage
    showDonationTicker: "readonly",
    htmx: "readonly",
    WebTransport: "readonly",
  },
  extends: ["eslint:recommended"],
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: "module",
  },
  rules: {
    // Recommended best practices & fixes for your current errors:
    "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }], // warn on unused vars, allow unused args starting with _
    "no-undef": "error",
    "no-prototype-builtins": "warn", // prefer Object.prototype.hasOwnProperty.call(...)
    "no-useless-escape": "warn",
    "no-empty": ["warn", { allowEmptyCatch: true }], // allow empty catch blocks
    // You can add more custom rules here as needed
  },
  ignorePatterns: [
    "*.min.js", // ignore all minified files
    "bundle.min.js",
    "socket.io.js",
    "alpine.min.js",
    "htmx.min.js",
  ],
};
