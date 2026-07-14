import { expect, test } from "@playwright/test";

test.describe("Homepage", () => {
  test("renders Tsubo header and search", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Find space with precision" })).toBeVisible();
    await expect(page.getByRole("searchbox")).toBeVisible();
    await expect(page.getByLabel("Display currency")).toBeVisible();
  });

  test("navigates to search page", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Search" }).click();
    await expect(page).toHaveURL(/\/search/);
  });
});
