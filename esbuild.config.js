// esbuild.config.js
const esbuild = require("esbuild");
const fs = require("fs");
const path = require("path");

// 1. Define paths for vendor and your own source code
const vendorFiles = [
  "app/static/js/alpine.min.js",
  "app/static/js/htmx.min.js",
  "app/static/js/socket.io.js",
  "app/static/js/confetti.js",
];

// (Optionally: Add your own authored JS here for true SaaS extensibility)
const appEntry = "app/static/js/src/app.js"; // <-- Create this file for your custom code!

const outputFile = "app/static/js/bundle.min.js";

const isDev = process.argv.includes("--dev");

// 2. Build your own JS (if exists)
async function buildAppJs() {
  // Only bundle if you have a src/app.js!
  if (!fs.existsSync(appEntry)) return null;
  const result = await esbuild.build({
    entryPoints: [appEntry],
    bundle: true,
    minify: !isDev,
    sourcemap: isDev,
    write: false, // We'll write it ourselves after concat
    format: "iife", // Safer for legacy browser support
    logLevel: "silent",
    define: {
      "process.env.NODE_ENV": isDev ? '"development"' : '"production"',
    },
    banner: {
      js: `/**\n * FundChamps Custom App JS Bundle\n * Built: ${new Date().toISOString()}\n */`,
    },
  });
  return result.outputFiles[0].text;
}

// 3. Final bundle: Concatenate vendor + your code, output to bundle.min.js
async function buildBundle() {
  try {
    // Read and concat all vendor files (in order)
    const vendorCode = vendorFiles
      .map((file) => fs.readFileSync(file, "utf8"))
      .join("\n");
    // Build your own code (if present)
    const appCode = (await buildAppJs()) || "";
    // Write the final bundle
    fs.writeFileSync(outputFile, `${vendorCode}\n${appCode}`);
    console.log(`✅ JS bundle created at ${outputFile}`);
  } catch (err) {
    console.error("❌ Error during build:", err);
    process.exit(1);
  }
}

// 4. Watch mode (for dev workflow)
async function watchBundle() {
  console.log("👀 Watching for JS changes...");
  // Watch appEntry and vendor files for changes
  const filesToWatch = vendorFiles.concat([appEntry]);
  filesToWatch.forEach((file) => {
    if (fs.existsSync(file)) {
      fs.watchFile(file, { interval: 300 }, buildBundle);
    }
  });
  await buildBundle();
}

// 5. Entry point (dev/prod)
if (isDev) {
  watchBundle();
} else {
  buildBundle();
}
