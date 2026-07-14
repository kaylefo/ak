import { test, expect } from "@playwright/test";

/**
 * Placeholder e2e spec — replace when apps/web is available.
 */
test.skip("homepage loads", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Tsubo/i);
});
