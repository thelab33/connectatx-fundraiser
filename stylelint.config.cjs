/** @type {import('stylelint').Config} */
module.exports = {
  extends: ["stylelint-config-standard"],
  rules: {
    // Tailwind & friends
    "at-rule-no-unknown": [true, { ignoreAtRules: [
      "tailwind","apply","layer","variants","responsive","screen","config","theme","plugin","reference"
    ]}],
    // Templated / utility-heavy CSS
    "no-invalid-position-at-import-rule": null,
    "selector-class-pattern": null,
    "declaration-block-single-line-max-declarations": null,
    "no-duplicate-selectors": null,
    "declaration-property-value-no-unknown": null,
    "property-no-deprecated": null,
    "number-max-precision": null,
    "no-descending-specificity": null
  }
};
