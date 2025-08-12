// build.js — bundles everything into app/static/js/bundle.min.js
import { build, context, analyzeMetafile } from 'esbuild';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import fs from 'node:fs/promises';

const __dirname = dirname(fileURLToPath(import.meta.url));

const isWatch = process.argv.includes('--watch');
const mode = process.env.NODE_ENV || (isWatch ? 'development' : 'production');
const isProd = mode === 'production';

// Path to the ESM wrapper for socket.io-client
// (create at app/static/js/vendor/socketio.mjs and export { io } default)
const SOCKETIO_VENDOR = resolve(__dirname, 'app/static/js/vendor/socketio.mjs');

// --- tiny alias plugin -------------------------------------------------------
const aliasPlugin = (map) => ({
  name: 'alias',
  setup(build) {
    const entries = Object.entries(map);
    build.onResolve({ filter: /.*/ }, (args) => {
      for (const [from, to] of entries) {
        if (args.path === from || args.path.endsWith('/' + from)) {
          return { path: to };
        }
      }
      return null;
    });
  },
});

// fail build in prod if there are warnings (keeps bundles clean)
const failOnWarnPlugin = {
  name: 'fail-on-warn',
  setup(build) {
    build.onEnd((result) => {
      if (isProd && result.warnings?.length) {
        console.error(`⚠️  Build finished with ${result.warnings.length} warning(s) in production. Failing.`);
        for (const w of result.warnings) {
          const loc = w.location
            ? `${w.location.file}:${w.location.line}:${w.location.column} `
            : '';
          console.error('  •', loc + w.text);
        }
        process.exit(1);
      }
    });
  },
};

const options = {
  entryPoints: ['app/static/js/app.entry.js'],
  outfile: 'app/static/js/bundle.min.js',
  platform: 'browser',
  format: 'iife',
  target: ['es2020'],
  bundle: true,
  sourcemap: isWatch,              // inline maps during dev/watch
  minify: isProd,
  treeShaking: true,
  legalComments: 'none',
  charset: 'utf8',
  mainFields: ['browser', 'module', 'main'],
  define: {
    'process.env.NODE_ENV': JSON.stringify(mode),
  },
  drop: isProd ? ['console', 'debugger'] : [],
  logLevel: 'info',
  // silence noisy eval msgs; socket.io CJS note is gone via alias below
  logOverride: {
    'direct-eval': 'silent',
    'commonjs-variable-in-esm': 'silent',
  },
  metafile: !!process.env.ANALYZE,
  banner: { js: '/* FundChamps bundle (c) */' },
  plugins: [
    // Map any legacy/socket imports to our ESM wrapper
    aliasPlugin({
      'socket.io.js': SOCKETIO_VENDOR,
      './socket.io.js': SOCKETIO_VENDOR,
      'app/static/js/socket.io.js': SOCKETIO_VENDOR,
    }),
    failOnWarnPlugin,
  ],
};

async function run() {
  try {
    if (isWatch) {
      const ctx = await context(options);
      await ctx.watch();
      console.log(`👀 esbuild watching (${mode})…`);
    } else {
      const result = await build(options);
      console.log('✅ JS bundle built: app/static/js/bundle.min.js');

      if (process.env.ANALYZE && result.metafile) {
        await fs.writeFile('app/static/js/bundle-meta.json', JSON.stringify(result.metafile, null, 2));
        const report = await analyzeMetafile(result.metafile, { verbose: true });
        await fs.writeFile('app/static/js/bundle-report.txt', report);
        console.log('📊 Wrote bundle-meta.json and bundle-report.txt');
      }
    }
  } catch (err) {
    console.error('❌ esbuild failed:', err);
    process.exit(1);
  }
}

run();

