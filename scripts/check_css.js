//!/usr/bin/env node
// scripts/check_css.js
// Minimal CSS sanity check used by `npm run css:verify` (ESM)

import { readFile, stat } from "node:fs/promises";
import { gzipSync, brotliCompressSync } from "node:zlib";
import { exit } from "node:process";

const target = process.env.CSS_OUT || "app/static/css/tailwind.min.css";

async function main() {
  try {
    const info = await stat(target);
    if (!info.isFile()) {
      console.error(`❌ Not a file: ${target}`);
      return exit(1);
    }

    const buf = await readFile(target);
    if (buf.length < 1000) {
      console.error(`❌ CSS looks too small (${buf.length} bytes): ${target}`);
      return exit(1);
    }

    const css = buf.toString("utf8");
    const mustHave = [".container", ".grid", ".flex", ".rounded", ".text-"];
    const missing = mustHave.filter((t) => !css.includes(t));
    if (missing.length >= mustHave.length) {
      console.error(
        "❌ CSS appears empty or malformed (common tokens missing).",
      );
      return exit(1);
    }

    const minBytes = Number(process.env.CSS_MIN_BYTES || 1000);
    if (buf.length < minBytes) {
      console.error(
        `❌ CSS looks too small (${buf.length} bytes < ${minBytes}): ${target}`,
      );
      return exit(1);
    }

    const gz = gzipSync(buf).length;
    const br = brotliCompressSync(buf).length;
    console.log(
      `✅ CSS OK: ${target}\n   size=${fmt(info.size)}  gzip=${fmt(gz)}  br=${fmt(br)}`,
    );
    exit(0);
  } catch (err) {
    console.error(`❌ CSS verify failed: ${err?.message || err}`);
    exit(1);
  }
}

function fmt(n) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(2)} MB`;
}

main();
