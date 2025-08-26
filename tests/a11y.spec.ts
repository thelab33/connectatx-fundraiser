import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'playwright-axe';

test('a11y: hero has no serious violations', async ({ page }) => {
  await page.goto('/');
  await injectAxe(page);
  await checkA11y(page, '#fc-hero', {
    detailedReport: true,
    axeOptions: { runOnly: ['wcag2a','wcag2aa'] }
  });
});

