// starforge.mjs — forge responsive hero assets with Sharp
// Usage:
//   node starforge.mjs images
//   SRC="static/images/connect-atx-team.jpg" OUTDIR="static/images/hero" node starforge.mjs images
//   node starforge.mjs lqip
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import url from "node:url";
import sharp from "sharp";

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));

// Resolve defaults
const repoRoot = path.resolve(__dirname, "..", "..");
const defaultSrcA = path.join(repoRoot, "app/static/images/connect-atx-team.jpg");
const defaultSrcB = path.join(repoRoot, "static/images/connect-atx-team.jpg");
const SRC = process.env.SRC
  ? path.resolve(repoRoot, process.env.SRC)
  : (fs.existsSync(defaultSrcA) ? defaultSrcA : defaultSrcB);

const guessOut = SRC.includes(path.sep + "app" + path.sep)
  ? path.join(repoRoot, "app/static/images/hero")
  : path.join(repoRoot, "static/images/hero");

const OUTDIR = path.resolve(repoRoot, process.env.OUTDIR || guessOut);
fs.mkdirSync(OUTDIR, { recursive: true });

const widths = [1920, 1280, 960];

function log(...args){ console.log("⭐ Starforge:", ...args); }
function warn(...args){ console.warn("⚠️  Starforge:", ...args); }

async function forgeImages(){
  if (!fs.existsSync(SRC)){
    warn("Source not found:", SRC);
    process.exitCode = 1;
    return;
  }
  log("Source:", SRC);
  log("Output:", OUTDIR);
  const base = "hero";

  // Ensure 16:9 cover crop, center by default
  for (const w of widths){
    const pipeline = sharp(SRC).resize({
      width: w,
      height: Math.round(w * 9 / 16),
      fit: "cover",
      position: "centre"
    });

    // AVIF
    const avifOut = path.join(OUTDIR, `${base}-${w}.avif`);
    await pipeline
      .clone()
      .avif({ quality: 62, effort: 4, chromaSubsampling: "4:2:0" })
      .toFile(avifOut);
    log("✓", path.relative(repoRoot, avifOut));

    // WEBP
    const webpOut = path.join(OUTDIR, `${base}-${w}.webp`);
    await pipeline
      .clone()
      .webp({ quality: 70, effort: 4 })
      .toFile(webpOut);
    log("✓", path.relative(repoRoot, webpOut));
  }
}

async function writeLQIP(){
  const lqipOut = path.join(OUTDIR, "hero-lqip.txt");
  const buf = await sharp(SRC)
    .resize({ width: 24, height: 24, fit: "cover", position: "centre" })
    .jpeg({ quality: 40 })
    .toBuffer();
  const dataUri = `data:image/jpeg;base64,${buf.toString("base64")}`;
  fs.writeFileSync(lqipOut, dataUri, "utf8");
  log("✓ LQIP", path.relative(repoRoot, lqipOut));
}

const cmd = (process.argv[2] || "images").toLowerCase();
if (cmd === "images"){
  forgeImages().then(writeLQIP).catch(err => { console.error(err); process.exitCode = 1; });
}else if (cmd === "lqip"){
  writeLQIP().catch(err => { console.error(err); process.exitCode = 1; });
}else{
  warn("Unknown command:", cmd, "(use: images | lqip)");
}
