#!/usr/bin/env node
import { promises as fs } from 'node:fs';
import path from 'node:path';

const cssPath = path.resolve('app/static/css/tailwind.min.css');

try {
  const buf = await fs.readFile(cssPath);
  const kb = (buf.byteLength / 1024).toFixed(1);
  console.log(`✅ CSS exists: ${cssPath} (${kb} kB)`);

  // Simple sanity checks (tweak as you like)
  const css = buf.toString();
  if (!css.includes('.container')) {
    console.warn('⚠️ Sanity check: .container not found (did purge strip too much?)');
  }
  process.exit(0);
} catch (e) {
  console.error(`❌ Missing CSS: ${cssPath}`);
  process.exit(2);
}
