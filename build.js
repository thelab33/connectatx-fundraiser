// build.js — hardened esbuild for FundChamps (Context API)
// Usage:
//   NODE_ENV=production node build.js
//   node build.js --watch
//   ANALYZE=1 BUNDLE_BUDGET_KB=350 node build.js

import { build, context, analyzeMetafile } from "esbuild";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import fs from "node:fs/promises";
import { createHash } from "node:crypto";
import zlib from "node:zlib";
import { execSync } from "node:child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));

/* ----------------------------- CLI / Env --------------------------------- */
const argv = process.argv.slice(2);
const hasFlag = (f) => argv.includes(f);
const getVal = (k, d = null) => {
  const m = argv.find((a) => a.startsWith(`--${k}=`));
  return m ? m.split("=")[1] : (process.env[k.toUpperCase()] ?? d);
};

const isWatch = hasFlag("--watch");
const mode = process.env.NODE_ENV || (isWatch ? "development" : "production");
const isProd = mode === "production";
const budgetKB =
  Number(
    getVal("budget", process.env.BUNDLE_BUDGET_KB || (isProd ? 350 : 0)),
  ) || 0;

const ENTRY = resolve(__dirname, "app/static/js/app.entry.js");
const OUTFILE = resolve(__dirname, "app/static/js/bundle.min.js");
const META_JSON = resolve(__dirname, "app/static/js/bundle-meta.json");
const META_TXT = resolve(__dirname, "app/static/js/bundle-report.txt");
const MANIFEST = resolve(__dirname, "app/static/asset-manifest.json");
const CSS_FILE = resolve(__dirname, "app/static/css/app.min.css");

/* -------------------------- Safety / Utilities --------------------------- */
const requireNode = 18;
const nodeMajor = Number(process.versions.node.split(".")[0] || 0);
if (nodeMajor < requireNode) {
  console.error(
    `❌ Node ${requireNode}+ required (found ${process.versions.node}).`,
  );
  process.exit(1);
}

function gitShort() {
  try {
    return execSync("git rev-parse --short HEAD", {
      stdio: ["ignore", "pipe", "ignore"],
    })
      .toString()
      .trim();
  } catch {
    return "nogit";
  }
}
const stamp = new Date().toISOString();
const git = gitShort();

const sha = (algo, buf) => createHash(algo).update(buf).digest("base64");
const gzipSize = (buf) => {
  try {
    return zlib.gzipSync(buf, { level: zlib.constants.Z_BEST_COMPRESSION })
      .length;
  } catch {
    return 0;
  }
};

/* ------------------------------- Helpers --------------------------------- */
async function fileMeta(absPath) {
  try {
    const buf = await fs.readFile(absPath);
    const rel = absPath.replace(__dirname + "/", "");
    return {
      path: rel,
      bytes: buf.length,
      gzipBytes: gzipSize(buf),
      sri: {
        sha256: `sha256-${sha("sha256", buf)}`,
        sha384: `sha384-${sha("sha384", buf)}`,
      },
    };
  } catch {
    return null;
  }
}

async function writeManifest({ jsMeta, cssMeta }) {
  const manifest = {
    version: { git, builtAt: stamp, mode },
    assets: {
      ...(jsMeta && { "js/bundle.min.js": jsMeta }),
      ...(cssMeta && { "css/app.min.css": cssMeta }),
    },
    sri: {
      ...(jsMeta && { "js/bundle.min.js": jsMeta.sri.sha384 }),
      ...(cssMeta && { "css/app.min.css": cssMeta.sri.sha384 }),
    },
  };
  await fs.mkdir(dirname(MANIFEST), { recursive: true });
  await fs.writeFile(MANIFEST, JSON.stringify(manifest, null, 2));
  return manifest;
}

/* ------------------------------ Post-build -------------------------------- */
async function postBuild(result) {
  try {
    // JS meta
    const jsMeta = await fileMeta(OUTFILE);
    if (!jsMeta) throw new Error(`Missing output: ${OUTFILE}`);

    // CSS meta (optional in dev)
    const cssMeta = await fileMeta(CSS_FILE);

    await writeManifest({ jsMeta, cssMeta });

    // Budget check (gzip)
    if (isProd && budgetKB > 0 && jsMeta.gzipBytes > budgetKB * 1024) {
      console.error(
        `❌ Bundle exceeds budget: ${(jsMeta.gzipBytes / 1024).toFixed(1)} KB gzip > ${budgetKB} KB`,
      );
      if (result?.metafile) {
        const sorted = Object.entries(result.metafile.outputs)
          .map(([file, info]) => ({ file, bytes: info.bytes }))
          .sort((a, b) => b.bytes - a.bytes)
          .slice(0, 10);
        console.error("Top output chunks/files by raw bytes:");
        for (const r of sorted)
          console.error(`  • ${r.file} ${(r.bytes / 1024).toFixed(1)} KB`);
      }
      process.exit(1);
    }

    console.log(
      `✅ JS: ${(jsMeta.bytes / 1024).toFixed(1)} KB raw, ${(jsMeta.gzipBytes / 1024).toFixed(1)} KB gzip` +
        (cssMeta
          ? `  |  CSS: ${(cssMeta.bytes / 1024).toFixed(1)} KB raw, ${(cssMeta.gzipBytes / 1024).toFixed(1)} KB gzip`
          : ""),
    );
  } catch (e) {
    console.error("postBuild error:", e);
  }
}

/* ------------------------------ Plugins ---------------------------------- */
// Fail on warnings in prod (keeps CI honest)
const failOnWarnPlugin = {
  name: "fail-on-warn",
  setup(b) {
    b.onEnd((result) => {
      if (isProd && result.warnings?.length) {
        console.error(
          `⚠️  Build finished with ${result.warnings.length} warning(s) in production. Failing.`,
        );
        for (const w of result.warnings) {
          const loc = w.location
            ? `${w.location.file}:${w.location.line}:${w.location.column} `
            : "";
          console.error("  •", loc + w.text);
        }
        process.exit(1);
      }
    });
  },
};

// Strip HMR guards in prod
const stripHMRPlugin = {
  name: "strip-hmr",
  setup(b) {
    b.onLoad({ filter: /\.[cm]?jsx?$/ }, async (args) => {
      let src = await fs.readFile(args.path, "utf8");
      if (isProd) {
        // naive guard stripper; safe for our usage
        src = src.replace(/if\s*\(\s*import\.meta.*?\{[\s\S]*?\}\s*/g, "");
      }
      return { contents: src, loader: args.path.endsWith("x") ? "jsx" : "js" };
    });
  },
};

// Run postBuild after each build/rebuild (+ optional analyze)
const postBuildPlugin = {
  name: "post-build",
  setup(b) {
    b.onEnd(async (result) => {
      await postBuild(result);
      if (!isWatch && process.env.ANALYZE && result?.metafile) {
        await fs.writeFile(META_JSON, JSON.stringify(result.metafile, null, 2));
        const report = await analyzeMetafile(result.metafile, {
          verbose: true,
        });
        await fs.writeFile(META_TXT, report);
        console.log("📊 Wrote bundle-meta.json and bundle-report.txt");
      }
    });
  },
};

/* ------------------------------ Esbuild opts ----------------------------- */
const options = {
  entryPoints: [ENTRY],
  outfile: OUTFILE,
  platform: "browser",
  format: isProd ? "iife" : "esm",
  target: ["es2020"],
  bundle: true,
  sourcemap: isWatch ? "inline" : false,
  minify: isProd,
  treeShaking: true,
  legalComments: "none",
  charset: "utf8",
  mainFields: ["browser", "module", "main"],
  define: { "process.env.NODE_ENV": JSON.stringify(mode) },
  drop: isProd ? ["console", "debugger"] : [],
  logLevel: "info",
  logOverride: {
    "direct-eval": "silent",
    "commonjs-variable-in-esm": "silent",
  },
  metafile: Boolean(process.env.ANALYZE),
  banner: { js: `/* FundChamps bundle | ${mode} | ${git} | ${stamp} */` },
  plugins: [failOnWarnPlugin, stripHMRPlugin, postBuildPlugin],
};

/* --------------------------------- Run ----------------------------------- */
async function run() {
  try {
    await fs.mkdir(dirname(OUTFILE), { recursive: true });

    if (isWatch) {
      const ctx = await context(options);
      await ctx.rebuild(); // triggers first postBuild
      await ctx.watch();
      console.log(`👀 esbuild watching (${mode})…`);

      const close = async () => {
        try {
          await ctx.dispose();
        } finally {
          process.exit(0);
        }
      };
      process.on("SIGINT", close);
      process.on("SIGTERM", close);
    } else {
      await build(options); // postBuild runs via plugin
      console.log("✅ JS bundle built:", OUTFILE);
    }
  } catch (err) {
    console.error("❌ esbuild failed:", err);
    process.exit(1);
  }
}

run();
