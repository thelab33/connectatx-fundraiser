import fs from "fs-extra";
import path from "path";
import fg from "fast-glob";
import postcss from "postcss";
import atImport from "postcss-import";
import cssnano from "cssnano";
import presetLite from "cssnano-preset-lite";
import pc from "picocolors";

/* -------------------------------------------
   StarForge CSS Audit — merge, dedupe, report
   ------------------------------------------- */
const CWD = process.cwd();
const CONFIG_PATH = path.join(CWD, "starforge.audit.config.json");
const cfg = JSON.parse(await fs.readFile(CONFIG_PATH, "utf8"));
const PURGE = process.env.PURGE === "1" || cfg.tailwind.purge === true;

const ENTRY = path.join(CWD, cfg.entry);
const OUT_DIR = path.join(CWD, cfg.outDir);
const REPORT_PATH = path.join(OUT_DIR, "starforge-audit.report.md");
const OUT_MERGED = path.join(OUT_DIR, "starforge.merged.css");
const OUT_REFACTORED = path.join(OUT_DIR, "input.refactored.css");
await fs.ensureDir(OUT_DIR);

const log = {
  info: (...a) => console.log(pc.cyan("i"), ...a),
  ok:   (...a) => console.log(pc.green("✔"), ...a),
  warn: (...a) => console.log(pc.yellow("!"), ...a),
  err:  (...a) => console.log(pc.red("✖"), ...a)
};

const normalize = s => s.replace(/\s+/g, " ").trim();
const scopeKey = (node) => {
  let p = node.parent; const chain = [];
  while (p && p.type !== "root") { if (p.type === "atrule") chain.unshift(`@${p.name} ${p.params || ""}`.trim()); p = p.parent; }
  return chain.join(" | ");
};

const collectContentClasses = async () => {
  const files = await fg(cfg.contentGlobs, { dot: false, cwd: CWD });
  const classSet = new Set(); const idSet = new Set();
  const CLASS_RE = /class(Name)?=["'`]{1}([^"'`]+)["'`]{1}/g;
  const TOKEN_RE = /[#.]([-_a-zA-Z0-9:\/\[\]%.]+)/g;
  for (const f of files) {
    const str = await fs.readFile(path.join(CWD, f), "utf8").catch(() => "");
    let m; while ((m = CLASS_RE.exec(str))) {
      const raw = m[2]; let t; TOKEN_RE.lastIndex = 0;
      while ((t = TOKEN_RE.exec(`.${raw}`))) { const val = t[1]; if (val.startsWith("#")) continue; classSet.add(val); }
    }
    const ID_RE = /id=["'`]([a-zA-Z0-9\-_:]+)["'`]/g;
    while ((m = ID_RE.exec(str))) idSet.add(m[1]);
  }
  for (const p of (cfg.tailwind.safeClassPatterns || [])) classSet.add(p);
  return { classSet, idSet };
};
const isSafeTW = (sel, patterns) => {
  try { return patterns.some(p => new RegExp(p).test(sel)); } catch { return false; }
};

const run = async () => {
  log.info("Reading", ENTRY);
  const cssRaw = await fs.readFile(ENTRY, "utf8");
  const imported = await postcss([atImport()]).process(cssRaw, { from: ENTRY });
  const root = imported.root;

  const seen = new Map();
  const conflicts = [];
  const dups = [];
  const importantCount = new Map();
  const zIndexMap = new Map();
  const layersSeen = new Set();

  const getLayerName = (node) => {
    let p = node.parent;
    while (p && p.type !== "root") {
      if (p.type === "atrule" && p.name === "layer") return p.params || "(unscoped)";
      p = p.parent;
    }
    return "(unscoped)";
  };

  root.walkRules(rule => {
    const layer = getLayerName(rule); layersSeen.add(layer);
    const scope = scopeKey(rule);
    const selectors = rule.selectors || [rule.selector];
    for (const sel of selectors) {
      const key = `${layer}__${scope}__${normalize(sel)}`;
      let bucket = seen.get(key);
      if (!bucket) {
        bucket = { layer, scope, selector: normalize(sel), decls: new Map(), origins: new Set(), count: 0 };
        seen.set(key, bucket);
      }
      bucket.count++;
      rule.walkDecls(decl => {
        const prop = decl.prop.trim().toLowerCase();
        const val = normalize(decl.value);
        const existing = bucket.decls.get(prop);
        if (existing && existing !== val) conflicts.push({ selector: bucket.selector, prop, values: [existing, val], scope: bucket.scope, layer: bucket.layer });
        bucket.decls.set(prop, val);
        if (decl.important) importantCount.set(bucket.selector, (importantCount.get(bucket.selector) || 0) + 1);
        if (prop === "z-index") { if (!zIndexMap.has(bucket.selector)) zIndexMap.set(bucket.selector, new Set()); zIndexMap.get(bucket.selector).add(val); }
      });
      if (rule.source?.input?.file) bucket.origins.add(path.relative(CWD, rule.source.input.file));
    }
  });

  const clean = postcss.root();
  (cfg.tailwind.keepDirectives || []).forEach(d => clean.append(postcss.parse(d)));

  const byLayer = {};
  for (const [, bucket] of seen) {
    const { layer, scope } = bucket;
    byLayer[layer] ||= {}; byLayer[layer][scope] ||= [];
    byLayer[layer][scope].push(bucket);
    if (bucket.count > 1) dups.push({ selector: bucket.selector, layer, scope, count: bucket.count });
  }

  let contentSets = { classSet: new Set(), idSet: new Set() };
  if (PURGE) { log.warn("Conservative purge enabled"); contentSets = await collectContentClasses(); }
  const safeTW = (sel) => isSafeTW(sel, cfg.tailwind.safeClassPatterns || []);

  const layerOrder = ["base", "components", "utilities"];
  const otherLayers = [...Object.keys(byLayer)].filter(l => !layerOrder.includes(l));
  const emitLayer = (layerName) => {
    if (!byLayer[layerName]) return;
    const layerRoot = postcss.atRule({ name: "layer", params: layerName });
    const scopes = Object.keys(byLayer[layerName]);
    if (cfg.merge.sortMediaQueries) scopes.sort();
    for (const scope of scopes) {
      const group = byLayer[layerName][scope];
      if (cfg.merge.sortSelectorsAlpha) group.sort((a,b)=>a.selector.localeCompare(b.selector));
      let container = layerRoot;
      if (scope) {
        scope.split(" | ").forEach(token => {
          if (!token) return;
          const [name, ...rest] = token.replace(/^@/, "").split(" ");
          const params = rest.join(" ").trim();
          const at = postcss.atRule({ name, params });
          container.append(at); container = at;
        });
      }
      for (const bucket of group) {
        if (PURGE) {
          const sels = bucket.selector.split(/\s*,\s*/);
          const keep = sels.some(s => {
            const mClass = s.match(/\.([_a-zA-Z0-9-:]+)/);
            const mId = s.match(/#([_a-zA-Z0-9-:]+)/);
            if (safeTW(s)) return true;
            if (mClass && contentSets.classSet.has(mClass[1])) return true;
            if (mId && contentSets.idSet.has(mId[1])) return true;
            return true; // conservative default
          });
          if (!keep) continue;
        }
        const rule = postcss.rule({ selector: bucket.selector });
        for (const [prop, val] of bucket.decls.entries()) rule.append(postcss.decl({ prop, value: val }));
        container.append(rule);
      }
    }
    if (layerRoot.nodes?.length) clean.append(layerRoot);
  };
  [...layerOrder, ...otherLayers].forEach(emitLayer);

  if (cfg.heroOverlaySafety) {
    clean.append(postcss.parse(`
/* --- StarForge overlay safety (kept last to win stacking) --- */
#fc-hero .fc-hero-overlay{
  position:absolute; inset:0; z-index:999;
  display:flex; flex-direction:column; gap:.75rem; align-items:center; text-align:center;
  padding:1rem clamp(1rem,2vw,1.6rem);
  background:linear-gradient(180deg, rgb(0 0 0 / 0%), rgb(0 0 0 / 68%) 42%, rgb(0 0 0 / 97%));
  color:#fff;
  transform:none !important;
}
:root.light #fc-hero .fc-hero-overlay{
  background:linear-gradient(180deg, rgb(255 255 255 / 0%), rgb(255 255 255 / 86%) 58%, rgb(255 255 255 / 96%));
  color:#111;
}
`));
  }

  const minified = await postcss([ cssnano({ preset: presetLite({ discardComments: { removeAll: true } }) }) ])
    .process(clean.toString(), { from: undefined });

  await fs.writeFile(OUT_MERGED, minified.css, "utf8");
  const header = `/* Auto-generated by StarForge CSS Audit
 - Merged & deduped from: ${path.relative(CWD, ENTRY)}
 - ${new Date().toISOString()}
*/\n`;
  const refactored = [
    header,
    ...cfg.tailwind.keepDirectives,
    "\n/* ---- Project CSS (merged) ---- */\n",
    minified.css
  ].join("\n");
  await fs.writeFile(OUT_REFACTORED, refactored, "utf8");

  const impHot = [...importantCount.entries()].sort((a,b)=>b[1]-a[1]).slice(0,20);
  const zStackHot = [...zIndexMap.entries()].map(([sel, vals])=>({sel, vals:[...vals]}))
    .filter(x => x.vals.length > 1 || x.vals.some(v => +v >= 100)).slice(0,30);

  const report = `# StarForge CSS Audit Report

**Entry:** \`${path.relative(CWD, ENTRY)}\`
**Output:** \`${path.relative(CWD, OUT_REFACTORED)}\`

- Total unique selector blocks: **${seen.size}**
- Exact duplicate blocks encountered: **${dups.length}**
- Conflicts (same selector+scope, different values): **${conflicts.length}**
- Layers seen: ${[...layersSeen].map(l => \`\\\`${l}\\\`\\\`).join(", ")}

---

## Top \`!important\` usage (by selector)
${impHot.map(([sel, n]) => `- \`${sel}\` — ${n}`).join("\n") || "_none_"}

## Potential z-index risks
${zStackHot.map(x => `- \`${x.sel}\` — values: ${x.vals.join(", ")}`).join("\n") || "_none_"}

## Duplicate blocks removed (sample)
${dups.slice(0, 40).map(d => `- \`${d.selector}\` @ \`${d.layer}\` | \`${d.scope}\` (count: ${d.count})`).join("\n") || "_none_"}

## Conflicts (same selector/scope, differing values)
${conflicts.slice(0, 60).map(c => `- \`${c.selector}\` @ \`${c.layer}\` | \`${c.scope}\` — **${c.prop}**: ${c.values.join(" → ")}`).join("\n") || "_none_"}

---

### Notes
- Tailwind directives preserved at top.
- Merged inside \`@layer base/components/utilities\` where present.
- Media/support chains ${cfg.merge.sortMediaQueries ? "sorted" : "kept"}.
- ${PURGE ? "**Purge enabled** (conservative; allowlist protects Tailwind/dynamic classes)." : "Purge disabled (report-only)."}
- Hero overlay safety appended at end: **${cfg.heroOverlaySafety ? "ON" : "OFF"}**.
`;
  await fs.writeFile(REPORT_PATH, report, "utf8");

  log.ok("Merged CSS:", path.relative(CWD, OUT_MERGED));
  log.ok("Refactored entry:", path.relative(CWD, OUT_REFACTORED));
  log.ok("Report:", path.relative(CWD, REPORT_PATH));
};

try { await run(); } catch (e) { log.err(e?.message || e); process.exit(1); }
