import plugin from "tailwindcss/plugin";
import forms from "@tailwindcss/forms";
import typography from "@tailwindcss/typography";
import aspect from "@tailwindcss/aspect-ratio";

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class", ".dark"],

  content: [
    "./app/templates/**/*.{html,jinja,jinja2}",
    "./app/static/js/**/*.{js,ts,mjs}",
    "./app/static/css/src/**/*.{html,css}",
    // Add more paths ONLY if you directly embed classnames there
  ],

  // --- SAFELIST for dynamic/custom classes & IDs ---
  safelist: [
    "sr-only",
    "bg-black",
    "bg-yellow-400",
    "text-yellow-400",
    "rounded-xl",
    "rounded-2xl",
    "shadow-gold-glow",
    "shadow-xl-gold",
    // For SaaS partials, sticky header, hero shell, sponsor rail, etc:
    "fc-header-grid",
    "__sentinel-header",
    "hero-shell",
    "fc-leaderband",
    // Animations
    {
      pattern: /^(motion-safe:)?animate-(kenburns|bounce-in|fade-in|sparkle|shine|spin(-reverse)?(-slow)?)$/,
    },
    // Gradients
    {
      pattern: /^(from|via|to)-(zinc|yellow|black|white|amber|gray)-(50|100|200|300|400|500|600|700|800|900|950)$/,
    },
    // Z-index helpers
    { pattern: /^z-(10|20|30|40|50|99|999|9999|99999)$/ },
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
        sans: [
          "Inter",
          "Montserrat",
          "Roboto",
          "Segoe UI",
          "Arial",
          "sans-serif",
        ],
      },
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
        "xl-gold": "0 20px 25px -5px rgba(250,204,21,.4), 0 10px 10px -5px rgba(250,204,21,.2)",
        "inner-glow": "inset 0 0 15px #facc15cc",
      },
      keyframes: {
        kenburns: {
          "0%": { transform: "scale(1.12) translateY(6px)", opacity: ".94" },
          "100%": { transform: "scale(1.01) translateY(0)", opacity: "1" },
        },
        "bounce-in": {
          "0%": { transform: "scale(.9) translateY(22px)", opacity: "0" },
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
        "brand-glass": "linear-gradient(180deg, rgba(20,20,20,.70), rgba(20,20,20,.86)), linear-gradient(125deg, color-mix(in srgb, var(--fc-brand, #facc15) 28%, transparent), rgba(255,255,255,.03))",
      },
      ringColor: {
        DEFAULT: "#facc15",
        "primary-focus": "#fbbf24",
        brand: "rgb(var(--fc-brand-rgb, 250 204 21) / 1)",
      },
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            color: theme("colors.zinc.200"),
            a: { color: theme("colors.yellow.300"), textDecoration: "none" },
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

  // --- Plugins (forms, typography, aspect, custom utilities) ---
  plugins: [
    forms({ strategy: "class" }),
    typography,
    aspect,
    plugin(({ addUtilities, addVariant, matchUtilities, theme }) => {
      // Brand helpers
      addUtilities({
        ".bg-brand": { backgroundColor: "rgb(var(--fc-brand-rgb, 250 204 21) / 1)" },
        ".text-brand": { color: "rgb(var(--fc-brand-rgb, 250 204 21) / 1)" },
        ".border-brand": { borderColor: "rgb(var(--fc-brand-rgb, 250 204 21) / 1)" },
        ".ring-brand": { "--tw-ring-color": theme("ringColor.brand") },
        ".focus-ring-primary": {
          outline: `2px solid ${theme("colors.primary")}`,
          outlineOffset: "4px",
        },
        ".shadow-xl-gold": { boxShadow: theme("boxShadow.xl-gold") },
        ".transition-smooth": {
          transitionProperty: `${theme("transitionProperty.colors")}, box-shadow, opacity`,
          transitionDuration: "300ms",
          transitionTimingFunction: theme("transitionTimingFunction.ease-in-out"),
        },
        ".bg-gold-gradient": { backgroundImage: theme("backgroundImage.gold-gradient") },
        ".bg-amber-gradient": { backgroundImage: theme("backgroundImage.amber-gradient") },
        ".bg-brand-glass": { backgroundImage: theme("backgroundImage.brand-glass") },
      });
      // iOS safe-area
      addUtilities({
        ".p-safe-b": { paddingBottom: "calc(env(safe-area-inset-bottom) + 0.5rem)" },
        ".p-safe-t": { paddingTop: "calc(env(safe-area-inset-top) + 0.5rem)" },
        ".p-safe-x": {
          paddingLeft: "calc(env(safe-area-inset-left) + 1rem)",
          paddingRight: "calc(env(safe-area-inset-right) + 1rem)",
        },
        ".m-safe-b": { marginBottom: "env(safe-area-inset-bottom)" },
      });
      // Variants
      addVariant("hocus", ["&:hover", "&:focus"]);
      addVariant("supports-hover", "@media (hover: hover)");
      ["current", "expanded", "selected", "pressed"].forEach(attr =>
        addVariant(`aria-${attr}`, `&[aria-${attr}="true"]`)
      );
      ["open", "active"].forEach(d =>
        addVariant(`data-${d}`, `&[data-${d}="true"]`)
      );
      addVariant("reduced-motion", "@media (prefers-reduced-motion: reduce)");
      // Shimmer utility
      matchUtilities(
        {
          shimmer: value => ({
            backgroundImage: `linear-gradient(110deg, ${value} 8%, rgba(255,255,255,.15) 18%, ${value} 33%)`,
            backgroundSize: "200% 100%",
            animation: "shine 1.8s linear infinite",
          }),
        },
        { values: { DEFAULT: "rgba(0,0,0,.12)" } }
      );
    }),
  ],

  corePlugins: { preflight: true },

  future: {
    hoverOnlyWhenSupported: true,
    optimizeUniversalDefaults: true,
  },
};

