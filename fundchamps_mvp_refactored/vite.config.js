import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
  root: ".",
  publicDir: "static/images",
  build: {
    outDir: "static/build",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, "static/js/main.js"),
        styles: path.resolve(__dirname, "static/css/app.css"),
      },
    },
  },
});
