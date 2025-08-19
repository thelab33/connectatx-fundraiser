import { defineConfig } from '@playwright/test';
export default defineConfig({
  use: { baseURL: process.env.BASE_URL || 'http://localhost:5000', headless: true },
  reporter: [['list'], ['html', { open: 'never' }]],
  timeout: 30_000,
});

