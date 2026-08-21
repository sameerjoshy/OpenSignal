import { test, expect } from "@playwright/test";

test.describe("Landing page", () => {
  test("renders hero, nav and value props", async ({ page }) => {
    await page.goto("/");

    // Brand + nav
    await expect(page.locator(".landing-brand").first()).toBeVisible();
    await expect(page.locator(".landing-nav-links")).toBeVisible();

    // Hero
    await expect(page.locator(".landing-hero-title")).toBeVisible();
    await expect(page.locator(".landing-hero-title")).toContainText(/qualified meetings|signaling intent/i);

    // Value props (outcome-driven)
    await expect(page.locator(".landing-value-item")).toHaveCount(3);
    await expect(page.locator(".landing-value-title", { hasText: "Skip the busywork" })).toBeVisible();
    await expect(page.locator(".landing-value-title", { hasText: "Reach them first" })).toBeVisible();
    await expect(page.locator(".landing-value-title", { hasText: "Book more meetings" })).toBeVisible();

    // CTAs
    await expect(page.locator("a", { hasText: "Start free" }).first()).toBeVisible();
  });

  test("sections render: product, outcomes, pricing, faq", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("#product")).toBeVisible();
    await expect(page.locator("#outcomes")).toBeVisible();
    await expect(page.locator("#pricing")).toBeVisible();
    await expect(page.locator("#faq")).toBeVisible();
    await expect(page.locator(".landing-price-card")).toHaveCount(3);
  });

  test("nav links scroll to sections", async ({ page }) => {
    await page.goto("/");
    await page.click(".landing-nav-links a[href='#pricing']");
    await expect(page.locator("#pricing")).toBeInViewport();
  });

  test("footer links present", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator(".landing-footer")).toBeVisible();
    await expect(page.locator(".landing-footer-copy")).toContainText("Signal360");
  });
});
