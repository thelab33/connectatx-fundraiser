import { test, expect } from '@playwright/test';

test.describe('Hero smoke', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('deduped & visible', async ({ page }) => {
    const heroes = page.locator('#fc-hero');
    await expect(heroes).toHaveCount(1);
    await expect(page.locator('#fc-hero-img')).toBeVisible();
  });

  test('countdown ticks', async ({ page }) => {
    const sec = page.locator('#fc-ct-sec');
    const v1 = await sec.innerText();
    await page.waitForTimeout(1100);
    const v2 = await sec.innerText();
    expect(v1).not.toEqual(v2);
  });

  test('updateHeroMeter API updates numbers, width, milestones', async ({ page }) => {
    await page.evaluate(() => window.updateHeroMeter?.(2500, 10000));
    await expect(page.locator('#fc-pct')).toHaveText(/25\.0/);
    await expect(page.locator('#fc-raised')).toContainText('2,500');
    // bar width ~25%
    const width = await page.locator('#fc-bar').evaluate(e => parseFloat(getComputedStyle(e).width));
    const wrapW = await page.locator('[role="progressbar"]').evaluate(e => parseFloat(getComputedStyle(e).width));
    const pct = Math.round((width / wrapW) * 100);
    expect(Math.abs(pct - 25)).toBeLessThanOrEqual(2);
    // milestone 25% active
    await expect(page.locator('#fc-ms-25').locator('..').first()).toHaveClass(/active/);
  });

  test('custom event path & ticker', async ({ page }) => {
    await page.evaluate(() => {
      dispatchEvent(new CustomEvent('fc:funds:update',{
        detail:{ raised: 5000, goal: 10000, sponsorName: 'QA Sponsor' }
      }));
    });
    await expect(page.locator('#fc-pct')).toHaveText(/50\.0/);
    await expect(page.locator('#fc-ticker')).toContainText('QA Sponsor');
  });

  test('quick donate buttons wire amount → url', async ({ page }) => {
    const first = page.locator('#fc-hero .fc-cta').first();
    const amount = await first.getAttribute('data-amount');
    // Intercept navigation to avoid leaving the page
    const nav = page.waitForEvent('framenavigated');
    await first.click();
    const event = await nav;
    expect(new URL(event.url()).searchParams.get('amount')).toBe(amount);
  });

  test('share button works (mock both paths)', async ({ page }) => {
    // Web Share path
    await page.addInitScript(() => { (navigator as any).share = async () => true; });
    await page.reload();
    await page.locator('#fc-share').click();

    // Clipboard fallback path
    await page.addInitScript(() => { delete (navigator as any).share; (navigator.clipboard as any) = { writeText: async ()=>true }; });
    await page.reload();
    await page.locator('#fc-share').click();
    await expect(page.locator('#fc-share-ok')).toBeVisible();
  });
});

