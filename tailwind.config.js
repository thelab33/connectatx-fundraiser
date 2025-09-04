// tailwind.config.js
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/templates/**/*.jinja",
    "./app/templates/**/*.jinja2",
    "./app/templates/**/*.j2",
    "./app/static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        brand: "rgb(var(--fc-brand-rgb) / <alpha-value>)",
      },
    },
  },
  plugins: [],
};
