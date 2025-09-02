/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.py", "./app/**/*.html", "./templates/**/*.html"],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/typography")],
};
