module.exports = {
  content: ["app/templates/**/*.html", "app/static/js/**/*.{js,mjs,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: { 50:"#FFFBEB",100:"#FEF3C7",300:"#FCD34D",500:"#F59E0B",600:"#D97706",900:"#78350F" }
      },
      fontFamily: {
        display: ["Inter","ui-sans-serif","system-ui"],
        body: ["Inter","ui-sans-serif","system-ui"]
      }
    }
  },
  plugins: [require("@tailwindcss/typography"), require("@tailwindcss/forms")]
};
