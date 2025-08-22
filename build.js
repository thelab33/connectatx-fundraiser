// build.js
require("esbuild")
  .build({
    entryPoints: ["app/static/js/app.js"], // your source JS file
    bundle: true,
    outfile: "app/static/js/main.js",
    minify: true,
    sourcemap: true,
  })
  .catch(() => process.exit(1));
