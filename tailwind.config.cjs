// tailwind.config.cjs — FundChamps Prestige (SV-Grade)

const forms = require("@tailwindcss/forms");
const typography = require("@tailwindcss/typography");
const aspect = require("@tailwindcss/aspect-ratio");

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class", ".dark"],
  content: [
    "./app/templates/**/*.{html,jinja,jinja2}",
    "./app/templates/partials/**/*.{html,jinja,jinja2}",
    "./app/templates/macros/**/*.{html,jinja,jinja2}",
    "./app/templates/admin/**/*.{html,jinja,jinja2}",
    "./app/static/js/**/*.{js,ts,mjs}",
    "./app/**/*.py"
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
        "2xl": "1440px"
      }
    },
    extend: {
      // ------------------ Brand System ------------------
      fontFamily: {
        sans: ["Inter","Montserrat","Roboto","Segoe UI","Arial","sans-serif"]
      },
      colors: {
        primary: "#facc15",
        "primary-gold": "#fbbf24",
        "primary-yellow": "#fde68a",
        "brand-black": "#09090b",

        // Semantic brand tokens → matches :root in brand.tokens.css
        surface: "var(--fc-surface, #ffffff)",
        text: "var(--fc-text, #111111)",
        accent: "var(--fc-accent, #facc15)",

        brand: {
          DEFAULT: "rgb(var(--fc-brand-rgb, 250 204 21) / <alpha-value>)"
        }
      },

      // ------------------ Effects ------------------
      boxShadow: {
        "gold-glow": "0 0 8px 2px #facc15, 0 0 24px 0 #fde68a44",
        glass: "0 4px 32px 0 rgba(250,204,21,0.06), 0 1.5px 4.5px rgba(60,60,60,0.05)",
        "xl-gold": "0 20px 25px -5px rgba(250, 204, 21, 0.4), 0 10px 10px -5px rgba(250, 204, 21, 0.2)",
        "inner-glow": "inset 0 0 15px #facc15cc"
      },

      // ------------------ Animations ------------------
      keyframes: {
        kenburns: {
          "0%": { transform: "scale(1.12) translateY(6px)", opacity: "0.94" },
          "100%": { transform: "scale(1.01) translateY(0)", opacity: "1" }
        },
        "bounce-in": {
          "0%": { transform: "scale(0.9) translateY(22px)", opacity: "0" },
          "70%": { transform: "scale(1.08) translateY(-3px)", opacity: "1" },
          "100%": { transform: "scale(1) translateY(0)", opacity: "1" }
        },
        shine: { "100%": { backgroundPosition: "200% center" } },
        sparkle: {
          "0%,100%": { opacity: ".8", transform: "scale(1)" },
          "60%": { opacity: "1", transform: "scale(1.28)" }
        },
        "fade-in": {
          "0%": { opacity: 0, transform: "translateY(30px)" },
          "100%": { opacity: 1, transform: "none" }
        }
      },
      animation: {
        kenburns: "kenburns 18s ease-in-out infinite",
        "bounce-in": "bounce-in .7s cubic-bezier(.22,1.61,.36,1) 1",
        shine: "shine 2.1s linear infinite",
        sparkle: "sparkle 1.3s ease-in-out infinite",
        "fade-in": "fade-in 1.5s cubic-bezier(.39,.575,.565,1) both"
      },

      // ------------------ Gradients ------------------
      backgroundImage: {
        "gold-gradient": "linear-gradient(90deg, #facc15 0%, #fbbf24 100%)",
        "amber-gradient": "linear-gradient(45deg, #fbbf24 0%, #fde68a 100%)",
        "brand-glass":
          "linear-gradient(180deg, rgba(20,20,20,.70), rgba(20,20,20,.86)), linear-gradient(125deg, color-mix(in srgb, var(--fc-brand, #facc15) 28%, transparent), rgba(255,255,255,.03))"
      },

      // ------------------ Utilities ------------------
      ringColor: {
        DEFAULT: "#facc15",
        "primary-focus": "#fbbf24",
        brand: "rgb(var(--fc-brand-rgb, 250 204 21) / 1)"
      },
      outline: {
        primary: ["2px solid #facc15", "4px"],
        brand: ["2px solid rgb(var(--fc-brand-rgb, 250 204 21) / 1)", "4px"]
      },
      transitionProperty: {
        colors: "color, background-color, border-color, text-decoration-color, fill, stroke",
        shadow: "box-shadow",
        opacity: "opacity"
      },
      transitionTimingFunction: {
        "ease-in-out": "cubic-bezier(0.4, 0, 0.2, 1)"
      },
      zIndex: {
        99: "99",
        999: "999",
        9999: "9999",
        99999: "99999"
      },

      // ------------------ Typography ------------------
      typography: (theme) => ({
        DEFAULT: {
          css: {
            color: theme("colors.zinc.200"),
            a: { color: theme("colors.yellow.300"), textDecoration: "none" },
            strong: { color: theme("colors.zinc.50") },
            h1: { color: theme("colors.yellow.300") },
            h2: { color: theme("colors.yellow.300") },
            h3: { color: theme("colors.yellow.200") },
            code: { color: theme("colors.yellow.200") }
          }
        },
        invert: {
          css: {
            color: theme("colors.zinc.300"),
            a: { color: theme("colors.yellow.300") }
          }
        }
      })
    }
  },
  plugins: [
    forms({ strategy: "class" }),
    typography,
    aspect
  ]
};

