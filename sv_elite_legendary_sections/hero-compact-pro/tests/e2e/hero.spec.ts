import { test, expect } from '@playwright/test';

test('hero loads, meter accessible, donate flows', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /Fuel the Season|Fund the Future/i })).toBeVisible();

  const meter = page.getByRole('meter');
  await expect(meter).toHaveAttribute('aria-valuemin', '0');
  await expect(meter).toHaveAttribute('aria-valuemax');
  await expect(meter).toHaveAttribute('aria-valuenow');

  // Quick amount decorate
  const quick = page.getByRole('link', { name: /\+?\$25/i }).first();
  const hrefBefore = await quick.getAttribute('href');
  await quick.dispatchEvent('pointerdown'); // triggers rewrite early
  const hrefAfter = await quick.getAttribute('href');
  expect(hrefAfter).not.toEqual(hrefBefore);
  expect(hrefAfter || '').toContain('utm_source=hero');

  // Mobile sticky appears <640px
  await page.setViewportSize({ width: 400, height: 800 });
  await expect(page.getByTestId('mobile-sticky')).toBeVisible();
});
