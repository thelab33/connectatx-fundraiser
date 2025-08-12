// scripts/check_css.js
import fs from 'fs';
const path = 'app/static/css/tailwind.min.css';
if (!fs.existsSync(path)) {
  console.error('❌ Missing', path);
  process.exit(1);
}
const size = fs.statSync(path).size;
console.log('✅ CSS ok:', path, Math.round(size / 1024) + 'KB');

