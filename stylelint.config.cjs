/** @type {import('stylelint').Config} */
module.exports = {
  // Use the opinionated base (already includes "recommended")
  extends: ["stylelint-config-standard"],

  // Let Stylelint parse <style> blocks in HTML/Jinja templates
  overrides: [
    {
      files: ["**/*.html", "**/*.jinja", "**/*.jinja2"],
      customSyntax: "postcss-html",
    },
    // If you keep any SCSS or nested syntax:
    {
      files: ["**/*.scss"],
      customSyntax: "postcss-scss",
    },
  ],

  rules: {
    /* ---------- Design tokens / CSS vars ---------- */
    "custom-property-pattern": [
      "^--(?:[a-z][a-z0-9-]*|_[a-z0-9-]+|step--\\d+)(?:[./][a-z0-9-]+)*$",
      { message: "Use kebab-case (e.g. --brand-color). Private vars may start with --_." },
    ],

    /* ---------- Tailwind / utility CSS ---------- */
    "at-rule-no-unknown": [
      true,
      {
        ignoreAtRules: [
          "tailwind",
          "apply",
          "layer",
          "variants",
          "responsive",
          "screen",
          "config",
          "theme",
          "plugin",
          "reference",
          "container",
          "property",
          "supports",
          "nest",
        ],
      },
    ],
    "no-invalid-position-at-import-rule": [
      true,
      { ignoreAtRules: ["tailwind", "layer", "use", "forward"] },
    ],

    /* ---------- Modern CSS ---------- */
    "function-no-unknown": [
      true,
      {
        ignoreFunctions: [
          "color-mix",
          "lab",
          "lch",
          "oklab",
          "oklch",
          "min",
          "max",
          "clamp",
          "env",
          "constant",
          "image-set",
        ],
      },
    ],
    "property-no-unknown": [
      true,
      {
        ignoreProperties: [
          "contain",
          "contain-intrinsic-size",
          "content-visibility",
          "scrollbar-gutter",
          "text-wrap",
          "view-transition-name",
          "animation-timeline",
          "view-timeline-name",
          "view-timeline-axis",
          "timeline-scope",
          "border-start-start-radius",
          "border-start-end-radius",
          "border-end-start-radius",
          "border-end-end-radius",
        ],
      },
    ],
    "media-feature-name-no-unknown": [
      true,
      {
        ignoreMediaFeatureNames: [
          "prefers-reduced-motion",
          "prefers-contrast",
          "prefers-color-scheme",
          "dynamic-range",
          "scripting",
          "hover",
          "any-hover",
          "pointer",
          "any-pointer",
          "view-timeline-axis",
        ],
      },
    ],
    "selector-pseudo-class-no-unknown": [
      true,
      { ignorePseudoClasses: ["where", "is", "has", "not", "nth-col", "nth-last-col", "global", "local"] },
    ],
    "selector-pseudo-element-no-unknown": [
      true,
      { ignorePseudoElements: ["view-transition", "view-transition-group", "view-transition-image-pair", "file-selector-button", "backdrop"] },
    ],

    /* ---------- Pragmatic relaxations for utilities ---------- */
    "selector-class-pattern": null,
    "keyframes-name-pattern": null,
    "declaration-block-single-line-max-declarations": null,
    "no-duplicate-selectors": null,
    "declaration-property-value-no-unknown": null,
    "property-no-deprecated": null,
    "number-max-precision": null,
    "no-descending-specificity": null,

    // Tailwind often uses keywords (e.g., currentColor) / variable-driven values
    "value-keyword-case": null,
  },

  // Keep CI green on generated/legacy bundles
  ignoreFiles: [
    "app/static/css/brand.tokens.css",
    "app/static/css/elite-upgrades.css",
    "app/static/css/fc_prestige*.css",
    "app/static/css/header-safe.css",
    "app/static/css/impact-lockers.css",
    "app/static/css/tiers-elite.css",
    "app/static/css/src/**/*.css",
  ],

  // Optional: enable property order (uncomment to use)
  /*
  plugins: ["stylelint-order"],
  rules: {
    ...,
    "order/properties-alphabetical-order": true
  }
  */
};

