// build.js — hardened esbuild for FundChamps
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
  return m ? m.split("=")[1] : process.env[k.toUpperCase()] ?? d;
};

const isWatch = hasFlag("--watch");
const mode = process.env.NODE_ENV || (isWatch ? "development" : "production");
const isProd = mode === "production";
const budgetKB =
  Number(getVal("budget", process.env.BUNDLE_BUDGET_KB || (isProd ? 350 : 0))) || 0;

const ENTRY = resolve(__dirname, "app/static/js/app.entry.js");
const OUTFILE = resolve(__dirname, "app/static/js/bundle.min.js");
const META_JSON = resolve(__dirname, "app/static/js/bundle-meta.json");
const META_TXT = resolve(__dirname, "app/static/js/bundle-report.txt");
const MANIFEST = resolve(__dirname, "app/static/asset-manifest.json");

/* -------------------------- Safety / Utilities --------------------------- */
const requireNode = 18;
const nodeMajor = Number(process.versions.node.split(".")[0] || 0);
if (nodeMajor < requireNode) {
  console.error(`❌ Node ${requireNode}+ required (found ${process.versions.node}).`);
  process.exit(1);
}

function gitShort() {
  try {
    return execSync("git rev-parse --short HEAD", { stdio: ["ignore", "pipe", "ignore"] })
      .toString()
      .trim();
  } catch {
    return "nogit";
  }
}
const stamp = new Date().toISOString();
const git = gitShort();

/* ------------------------------ Plugins ---------------------------------- */
const failOnWarnPlugin = {
  name: "fail-on-warn",
  setup(b) {
    b.onEnd((result) => {
      if (isProd && result.warnings?.length) {
        console.error(
          `⚠️  Build finished with ${result.warnings.length} warning(s) in production. Failing.`
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

// strip out HMR `import.meta.hot` in prod to silence warnings
const stripHMRPlugin = {
  name: "strip-hmr",
  setup(b) {
    b.onLoad({ filter: /\.js$/ }, async (args) => {
      let src = await fs.readFile(args.path, "utf8");
      if (isProd) {
        src = src.replace(/if\s*\(import\.meta.*?\{[\s\S]*?\}\s*/g, "");
      }
      return { contents: src, loader: "js" };
    });
  },
};

/* ------------------------------ Esbuild opts ----------------------------- */
const options = {
  entryPoints: [ENTRY],
  outfile: OUTFILE,
  platform: "browser",
  format: isProd ? "iife" : "esm", // dev keeps import.meta, prod strips & uses iife
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
  metafile: !!process.env.ANALYZE,
  banner: { js: `/* FundChamps bundle | ${mode} | ${git} | ${stamp} */` },
  plugins: [failOnWarnPlugin, stripHMRPlugin],
};

/* ----------------------------- Post-build -------------------------------- */
const sha = (algo, buf) => createHash(algo).update(buf).digest("base64");
const gzipSize = (buf) => {
  try {
    return zlib.gzipSync(buf, { level: zlib.constants.Z_BEST_COMPRESSION }).length;
  } catch {
    return 0;
  }
};

async function writeManifest({ bytes, gzipBytes, sha256, sha384 }) {
  const manifest = {
    version: { git, builtAt: stamp, mode },
    js: {
      bundle: {
        path: OUTFILE.replace(__dirname + "/", ""),
        bytes,
        gzipBytes,
        sri: { sha256: `sha256-${sha256}`, sha384: `sha384-${sha384}` },
      },
    },
  };
  await fs.mkdir(dirname(MANIFEST), { recursive: true });
  await fs.writeFile(MANIFEST, JSON.stringify(manifest, null, 2));
  return manifest;
}

async function postBuild(result) {
  const out = await fs.readFile(OUTFILE);
  const bytes = out.length;
  const gzipBytes = gzipSize(out);
  const sha256 = sha("sha256", out);
  const sha384 = sha("sha384", out);

  await writeManifest({ bytes, gzipBytes, sha256, sha384 });

  if (isProd && budgetKB > 0 && gzipBytes > budgetKB * 1024) {
    console.error(
      `❌ Bundle exceeds budget: ${(gzipBytes / 1024).toFixed(1)} KB gzip > ${budgetKB} KB`
    );
    if (result?.metafile) {
      const sorted = Object.entries(result.metafile.outputs)
        .map(([file, info]) => ({ file, bytes: info.bytes }))
        .sort((a, b) => b.bytes - a.bytes)
        .slice(0, 10);
      console.error("Top output chunks/files by raw bytes:");
      for (const r of sorted) console.error(`  • ${r.file} ${(r.bytes / 1024).toFixed(1)} KB`);
    }
    process.exit(1);
  }

  console.log(
    `✅ JS bundle: ${(bytes / 1024).toFixed(1)} KB raw, ${(gzipBytes / 1024).toFixed(1)} KB gzip`
  );
}

/* --------------------------------- Run ----------------------------------- */
async function run() {
  try {
    await fs.mkdir(dirname(OUTFILE), { recursive: true });

    if (isWatch) {
      const ctx = await context(options);
      await ctx.watch({
        onRebuild(err, res) {
          if (err) {
            console.error("❌ Rebuild failed:", err);
          } else {
            console.log("🔁 Rebuilt at", new Date().toLocaleTimeString());
            postBuild(res).catch((e) => console.error("postBuild error:", e));
          }
        },
      });
      console.log(`👀 esbuild watching (${mode})…`);
      const res = (await ctx.rebuild?.().catch(() => null)) || null;
      if (res) await postBuild(res);
    } else {
      const result = await build(options);
      console.log("✅ JS bundle built:", OUTFILE);
      await postBuild(result);

      if (process.env.ANALYZE && result.metafile) {
        await fs.writeFile(META_JSON, JSON.stringify(result.metafile, null, 2));
        const report = await analyzeMetafile(result.metafile, { verbose: true });
        await fs.writeFile(META_TXT, report);
        console.log("📊 Wrote bundle-meta.json and bundle-report.txt");
      }
    }
  } catch (err) {
    console.error("❌ esbuild failed:", err);
    process.exit(1);
  }
}

run();

