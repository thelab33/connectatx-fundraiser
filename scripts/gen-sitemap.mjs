import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);

const SITE = (process.argv[2] || 'http://localhost:8080').replace(/\/+$/,'');
const OUT  = process.argv[3] || path.join(__dirname, '..', 'app', 'static', 'sitemap.xml');
const TPL  = path.join(__dirname, '..', 'app', 'templates');

function guessRoute(file) {
  const name = path.basename(file);
  if (name === 'index.html') return '/';
  return '/' + name.replace(/\.html$/,'');
}

function collectHtml(dir) {
  const out = [];
  const walk = (d) => {
    for (const entry of fs.readdirSync(d, {withFileTypes: true})) {
      const p = path.join(d, entry.name);
      if (entry.isDirectory()) walk(p);
      else if (entry.isFile() && /\.html$/.test(entry.name)) out.push(p);
    }
  };
  if (fs.existsSync(dir)) walk(dir);
  return out;
}

const files = collectHtml(TPL);
const urls = files
  .map(guessRoute)
  .filter((v, i, a) => a.indexOf(v) === i) // de-dupe
  .sort();

const items = urls.map(u => `  <url><loc>${SITE}${u}</loc></url>`).join('\n');
const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${items}
</urlset>
`;
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, xml, 'utf8');
console.log('Wrote sitemap:', OUT, 'entries:', urls.length);
