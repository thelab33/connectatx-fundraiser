module.exports = {
  extends: ["stylelint-config-recommended", "stylelint-config-prettier"],
  plugins: ["stylelint-tailwindcss"],
  rules: {
    "tailwindcss/no-custom-classname": true,
    "color-no-invalid-hex": true,
    "declaration-no-important": true,
  },
};
