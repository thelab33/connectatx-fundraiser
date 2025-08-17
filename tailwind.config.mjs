/** =============================================================================
 * Tailwind CSS Config — FundChamps Elite
 * Mobile-first, SaaS-optimized, production-ready
 * ============================================================================= */
import forms from "@tailwindcss/forms";
import typography from "@tailwindcss/typography";
import aspect from "@tailwindcss/aspect-ratio";

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./app/templates/**/*.html",
    "./app/templates/**/*.jinja",
    "./app/templates/**/*.jinja2",
    "./app/templates/**/*.j2",
    "./app/static/js/**/*.js",
    "./app/static/js/**/*.mjs",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["InterVariable", "Inter", "ui-sans-serif", "system-ui"],
        display: ["Lexend", "ui-sans-serif"],
      },
      colors: {
        brand: {
          DEFAULT: "#facc15",
          dark: "#ca8a04",
          light: "#fde047",
        },
        gray: {
          950: "#0a0a0a",
        },
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            "--tw-prose-body": theme("colors.gray.800"),
            "--tw-prose-headings": theme("colors.gray.950"),
            "--tw-prose-links": theme("colors.brand.DEFAULT"),
            "--tw-prose-bold": theme("colors.gray.950"),
          },
        },
      }),
    },
  },
  plugins: [forms, typography, aspect],
};
