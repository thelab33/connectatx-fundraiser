module.exports = {
  content: [
    "./app/templates/**/*.{html,jinja,jinja2}",
    "./app/partials/**/*.{html,jinja,jinja2}",
    "./app/static/js/**/*.{js,ts}"
  ],
  css: [
    "./app/static/css/fc_elite.css",
    "./app/static/css/starforge-additions.css"
  ],
  output: "./app/static/css/purged", // cleaned files go here
  safelist: [
    // add anything generated dynamically or injected via JS
    "is-visible",
    "active",
    /^fc-/,
    /^sf-/
  ],
};

