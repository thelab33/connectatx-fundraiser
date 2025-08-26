// tailwind.config.mjs
import plugin from "tailwindcss/plugin";
import forms from "@tailwindcss/forms";
import typography from "@tailwindcss/typography";
import aspect from "@tailwindcss/aspect-ratio";

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class", ".dark"],

  content: [
    "./app/templates/**/*.{html,jinja,jinja2}",
    "./app/templates/partials/**/*.{html,jinja,jinja2}",
    "./app/templates/macros/**/*.{html,jinja,jinja2}",
    "./app/templates/admin/**/*.{html,jinja,jinja2}",
    "./app/static/js/**/*.{js,ts,mjs}",
    "./app/static/css/src/**/*.{html,css}",
    "./app/**/*.py",
    "./app/static/data/**/*.{json,txt}",
  ],

  // Keep only classes we *know* we need + dynamic anim/gradient ranges
  safelist: [
    "bg-zinc-950", "bg-zinc-900", "bg-black",
    "bg-yellow-400", "text-yellow-400",
    "rounded-xl", "rounded-2xl", "sr-only",
    "shadow-gold-glow", "shadow-xl-gold",
    // animation (optionally with motion-safe: prefix)
    { pattern: /^(motion-safe:)?animate-(kenburns|bounce-in|fade-in|sparkle|shine|spin(?:-reverse)?(?:-slow)?)$/ },
    // gradient color helpers used across templates
    { pattern: /^(from|via|to)-(zinc|yellow|black|white|amber|gray)-(50|100|200|300|400|500|600|700|800|900|950)$/ },
    // arbitrary z helpers sometimes injected via data-ui
    "z-10","z-20","z-30","z-40","z-50","z-99","z-999","z-9999","z-99999",
  ],

  theme: {
    container: {
      center: true,
      padding: "1rem",
      screens: {
        xs: "475px",
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
        "2xl": "1440px",
      },
    },

    extend: {
      fontFamily: {
        sans: ["Inter", "Montserrat", "Roboto", "Segoe UI", "Arial", "sans-serif"],
      },

      // Brand via CSS var with alpha support
      colors: {
        primary: "#facc15",
        "primary-gold": "#fbbf24",
        "primary-yellow": "#fde68a",
        "brand-black": "#09090b",
        brand: {
          DEFAULT: "rgb(var(--fc-brand-rgb, 250 204 21) / <alpha-value>)",
        },
      },

      boxShadow: {
        "gold-glow": "0 0 8px 2px #facc15, 0 0 24px 0 #fde68a44",
        glass: "0 4px 32px 0 rgba(250,204,21,0.06), 0 1.5px 4.5px rgba(60,60,60,0.05)",
        "xl-gold": "0 20px 25px -5px rgba(250, 204, 21, 0.4), 0 10px 10px -5px rgba(250, 204, 21, 0.2)",
        "inner-glow": "inset 0 0 15px #facc15cc",
      },

      keyframes: {
        kenburns: {
          "0%": { transform: "scale(1.12) translateY(6px)", opacity: "0.94" },
          "100%": { transform: "scale(1.01) translateY(0)", opacity: "1" },
        },
        "bounce-in": {
          "0%": { transform: "scale(0.9) translateY(22px)", opacity: "0" },
          "70%": { transform: "scale(1.08) translateY(-3px)", opacity: "1" },
          "100%": { transform: "scale(1) translateY(0)", opacity: "1" },
        },
        shine: { "100%": { backgroundPosition: "200% center" } },
        sparkle: {
          "0%,100%": { opacity: ".8", transform: "scale(1)" },
          "60%": { opacity: "1", transform: "scale(1.28)" },
        },
        "fade-in": {
          "0%": { opacity: 0, transform: "translateY(30px)" },
          "100%": { opacity: 1, transform: "none" },
        },
      },

      animation: {
        kenburns: "kenburns 18s ease-in-out infinite",
        "bounce-in": "bounce-in .7s cubic-bezier(.22,1.61,.36,1) 1",
        shine: "shine 2.1s linear infinite",
        sparkle: "sparkle 1.3s ease-in-out infinite",
        "fade-in": "fade-in 1.5s cubic-bezier(.39,.575,.565,1) both",
      },

      backgroundImage: {
        "gold-gradient": "linear-gradient(90deg, #facc15 0%, #fbbf24 100%)",
        "amber-gradient": "linear-gradient(45deg, #fbbf24 0%, #fde68a 100%)",
        "brand-glass":
          "linear-gradient(180deg, rgba(20,20,20,.70), rgba(20,20,20,.86)), linear-gradient(125deg, color-mix(in srgb, var(--fc-brand, #facc15) 28%, transparent), rgba(255,255,255,.03))",
      },

      ringColor: {
        DEFAULT: "#facc15",
        "primary-focus": "#fbbf24",
        brand: "rgb(var(--fc-brand-rgb, 250 204 21) / 1)",
      },

      outline: {
        primary: ["2px solid #facc15", "4px"],
        brand: ["2px solid rgb(var(--fc-brand-rgb, 250 204 21) / 1)", "4px"],
      },

      transitionProperty: {
        colors:
          "color, background-color, border-color, text-decoration-color, fill, stroke",
        shadow: "box-shadow",
        opacity: "opacity",
      },

      transitionTimingFunction: {
        "ease-in-out": "cubic-bezier(0.4, 0, 0.2, 1)",
      },

      zIndex: {
        99: "99",
        999: "999",
        9999: "9999",
        99999: "99999",
      },

      // Typography defaults tuned for dark backgrounds
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            color: theme("colors.zinc.200"),
            a: { color: theme("colors.yellow.300"), "text-decoration": "none" },
            strong: { color: theme("colors.zinc.50") },
            h1: { color: theme("colors.yellow.300") },
            h2: { color: theme("colors.yellow.300") },
            h3: { color: theme("colors.yellow.200") },
            code: { color: theme("colors.yellow.200") },
          },
        },
        invert: {
          css: {
            color: theme("colors.zinc.300"),
            a: { color: theme("colors.yellow.300") },
          },
        },
      }),
    },
  },

  plugins: [
    // Use forms in "class" mode to avoid global style overrides
    forms({ strategy: "class" }),
    typography,
    aspect,

    // Custom utilities/variants
    plugin(function ({ addUtilities, addVariant, matchUtilities, theme, e }) {
      // Brand helpers (map to CSS var --fc-brand or fallback)
      addUtilities(
        {
          ".bg-brand": { backgroundColor: "rgb(var(--fc-brand-rgb, 250 204 21) / 1)" },
          ".text-brand": { color: "rgb(var(--fc-brand-rgb, 250 204 21) / 1)" },
          ".border-brand": { borderColor: "rgb(var(--fc-brand-rgb, 250 204 21) / 1)" },
          ".ring-brand": { "--tw-ring-color": theme("ringColor.brand") },
          ".focus-ring-primary": { outline: `2px solid ${theme("colors.primary")}`, outlineOffset: "4px" },
          ".shadow-xl-gold": { boxShadow: theme("boxShadow.xl-gold") },
          ".transition-smooth": {
            transitionProperty: `${theme("transitionProperty.colors")}, box-shadow, opacity`,
            transitionDuration: "300ms",
            transitionTimingFunction: theme("transitionTimingFunction.ease-in-out"),
          },
          ".bg-gold-gradient": { backgroundImage: theme("backgroundImage.gold-gradient") },
          ".bg-amber-gradient": { backgroundImage: theme("backgroundImage.amber-gradient") },
          ".bg-brand-glass": { backgroundImage: theme("backgroundImage.brand-glass") },
        },
        ["responsive", "hover", "focus", "focus-visible"]
      );

      // iOS safe-area padding/margin shorthands
      addUtilities(
        {
          ".p-safe-b": { paddingBottom: "calc(env(safe-area-inset-bottom) + 0.5rem)" },
          ".p-safe-t": { paddingTop: "calc(env(safe-area-inset-top) + 0.5rem)" },
          ".p-safe-x": {
            paddingLeft: "calc(env(safe-area-inset-left) + 1rem)",
            paddingRight: "calc(env(safe-area-inset-right) + 1rem)",
          },
          ".m-safe-b": { marginBottom: "env(safe-area-inset-bottom)" },
        },
        ["responsive"]
      );

      // Data/ARIA/state variants that recur in your UI
      addVariant("hocus", ["&:hover", "&:focus"]);
      addVariant("supports-hover", "@media (hover: hover)");
      addVariant("aria-current", '&[aria-current="page"]');
      addVariant("aria-expanded", '&[aria-expanded="true"]');
      addVariant("aria-selected", '&[aria-selected="true"]');
      addVariant("aria-pressed", '&[aria-pressed="true"]');
      addVariant("data-open", '&[data-open="true"]');
      addVariant("data-active", '&[data-active="true"]');

      // Opt-in reduced-motion variant alias (motion-reduce is built-in; this mirrors it)
      addVariant("reduced-motion", "@media (prefers-reduced-motion: reduce)");

      // Shimmer utility (used by .shine keyframe sections)
      matchUtilities(
        {
          shimmer: (value) => ({
            backgroundImage:
              `linear-gradient(110deg, ${value} 8%, rgba(255,255,255,.15) 18%, ${value} 33%)`,
            backgroundSize: "200% 100%",
            animation: "shine 1.8s linear infinite",
          }),
        },
        { values: { DEFAULT: "rgba(0,0,0,.12)" } }
      );
    }),
  ],

  corePlugins: {
    preflight: true,
  },

  future: {
    hoverOnlyWhenSupported: true,
    optimizeUniversalDefaults: true,
  },
};

