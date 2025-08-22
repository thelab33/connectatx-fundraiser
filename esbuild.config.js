const esbuild = require('esbuild');

// Paths to the JS files to bundle
const inputFiles = [
  'app/static/js/alpine.min.js',
  'app/static/js/htmx.min.js',
  'app/static/js/socket.io.js',
  'app/static/js/confetti.js',
];

// Output path for the bundled JS file
const outputFile = 'app/static/js/bundle.min.js';

// Common configuration for esbuild
const commonConfig = {
  entryPoints: inputFiles,
  outfile: outputFile,
  minify: true,
  bundle: true,
  sourcemap: false,  // Set to true for production or debugging
  logLevel: 'info',
  define: {
    'process.env.NODE_ENV': '"production"', // Define production environment
  },
};

// Build the JavaScript bundle for production
async function buildJS() {
  try {
    await esbuild.build({
      ...commonConfig,
      sourcemap: false,  // No sourcemaps for production
    });
    console.log('JavaScript bundle built successfully!');
  } catch (err) {
    console.error('Error during build:', err);
    process.exit(1);
  }
}

// Watch mode for auto-rebuilding during development
async function watchJS() {
  try {
    await esbuild.build({
      ...commonConfig,
      sourcemap: true,  // Enable sourcemaps in watch mode for easier debugging
      watch: {
        onRebuild(error, result) {
          if (error) {
            console.error('Watch build failed:', error);
          } else {
            console.log('Rebuild succeeded:', result);
          }
        },
      },
    });
    console.log('Watching for changes...');
  } catch (err) {
    console.error('Error during watch build:', err);
    process.exit(1);
  }
}

// Determine the build mode: production (build) or development (watch)
const isDevelopment = process.argv.includes('--dev');

if (isDevelopment) {
  watchJS(); // Run in watch mode for development
} else {
  buildJS(); // Run a single build for production
}

