/** @type {import('stylelint').Config} */
module.exports = {
  extends: [
    "stylelint-config-standard",
    "stylelint-config-recommended",
  ],

  rules: {
    // ✅ Custom properties: brand tokens, private vars, steps, segmented
    "custom-property-pattern": [
      "^--(?:[a-z][a-z0-9-]*|_[a-z0-9-]+|step--\\d+)(?:[./][a-z0-9-]+)*$",
      { message: "Use kebab-case (e.g. --brand-color). Private vars may start with --_." }
    ],

    // 🌀 Tailwind / utility CSS
    "at-rule-no-unknown": [
      true,
      {
        ignoreAtRules: [
          "tailwind", "apply", "layer", "variants",
          "responsive", "screen", "config",
          "theme", "plugin", "reference",
          "container", "property", "supports",
        ],
      },
    ],

    // 🎨 Modern CSS features you use
    "function-no-unknown": [
      true,
      { ignoreFunctions: ["color-mix", "lab", "lch", "oklab", "oklch", "min", "max", "clamp"] },
    ],
    "property-no-unknown": [
      true,
      {
        ignoreProperties: [
          "contain", "contain-intrinsic-size", "content-visibility",
          "scrollbar-gutter", "text-wrap",
          "view-timeline-name", "view-timeline-axis",
          "animation-timeline", "timeline-scope",
        ],
      },
    ],
    "media-feature-name-no-unknown": [
      true,
      {
        ignoreMediaFeatureNames: [
          "prefers-reduced-motion", "prefers-contrast", "prefers-color-scheme",
          "dynamic-range", "scripting", "hover", "any-hover", "pointer", "any-pointer",
        ],
      },
    ],

    // 🚦 Lint only what matters; unblock aesthetics
    "selector-class-pattern": null,
    "keyframes-name-pattern": null,
    "declaration-block-single-line-max-declarations": null,
    "no-duplicate-selectors": null,
    "declaration-property-value-no-unknown": null,
    "property-no-deprecated": null,
    "number-max-precision": null,
    "no-descending-specificity": null,
  },

  ignoreFiles: [
    // 🚫 Ignore legacy / generated CSS
    "app/static/css/brand.tokens.css",
    "app/static/css/elite-upgrades.css",
    "app/static/css/fc_prestige*.css",
    "app/static/css/header-safe.css",
    "app/static/css/impact-lockers.css",
    "app/static/css/tiers-elite.css",
    "app/static/css/src/**/*.css",
  ],
};

