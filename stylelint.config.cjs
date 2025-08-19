// stylelint.config.cjs
module.exports = {
  extends: ["stylelint-config-standard"],
  rules: {
    "no-empty-source": null,
    "color-hex-length": "short",
    "selector-class-pattern": null
  },
  ignoreFiles: [
    "node_modules/**",
    "static/vendor/**",
    "**/*.min.css"
  ]
};

