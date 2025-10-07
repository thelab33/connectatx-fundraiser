import fs from "node:fs";
import path from "node:path";
import { globby } from "globby";
import sharp from "sharp";

const SRC = process.argv[2] || "app/static/images";
const OUT = process.argv[3] || path.join(SRC, "optimized");

await fs.promises.mkdir(OUT, { recursive: true });

const patterns = ["**/*.jpg","**/*.jpeg","**/*.png"].map(p =>
  path.join(SRC, p).replaceAll("\\","/")
);

const files = await globby(patterns, { onlyFiles: true, absolute: true });

let ok = 0, fail = 0;
for (const file of files) {
  const rel = path.relative(SRC, file);
  const base = path.join(OUT, rel).replace(/\.(jpe?g|png)$/i, "");
  await fs.promises.mkdir(path.dirname(base), { recursive: true });
  try {
    const img = sharp(file);
    await img.clone().webp({ quality: 82, effort: 6 }).toFile(base + ".webp");
    await img.clone().avif({ quality: 55, effort: 6 }).toFile(base + ".avif");
    ok++;
  } catch (e) {
    console.error("optimize fail:", rel, e.message);
    fail++;
  }
}
console.log(`optimized: ${ok} images, failed: ${fail}, out: ${OUT}`);
