import { test, expect } from "@playwright/test";

const PASSWORD = "password123";

test.describe("Settings / services", () => {
  test.beforeEach(async ({ page }) => {
    const email = `e2e-svc-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.com`;
    await page.addInitScript(() => localStorage.setItem("onboarding_done", "1"));
    await page.goto("/signup");
    await page.fill("#fullName", "Svc User");
    await page.fill("#email", email);
    await page.fill("#password", PASSWORD);
    await page.click('button[type="submit"]:has-text("Create account")');
    // onboarding_done is set via init script, so signup redirects to the dashboard; wait for auth to settle
    await expect(page.locator(".page-title", { hasText: "Dashboard" })).toBeVisible();
    await page.goto("/settings");
    await expect(page.locator(".page-title", { hasText: "Connected services" })).toBeVisible();
  });

  test("all services render with correct badges", async ({ page }) => {
    const cards = page.locator(".service-card");
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(9);

    // Keyless SEC EDGAR shows as available with a verify button (not Connect)
    const secCard = page.locator(".service-card", { hasText: "SEC EDGAR" });
    await expect(secCard).toBeVisible();
    await expect(secCard.locator("button", { hasText: "Verify connection" })).toBeVisible();

    // DeepSeek connectable with a key input
    await page.locator(".service-card", { hasText: "DeepSeek" }).locator("button", { hasText: "Connect" }).click();
    await expect(page.locator(".modal")).toBeVisible();
    await expect(page.locator(".modal input[type='password']")).toHaveCount(1);
    await page.locator(".modal").locator("button", { hasText: "Cancel" }).click();
    await expect(page.locator(".modal")).not.toBeVisible();
  });

  test("mailgun connect form includes domain field", async ({ page }) => {
    await page.locator(".service-card", { hasText: "Mailgun" }).locator("button", { hasText: "Connect" }).click();
    await expect(page.locator(".modal")).toBeVisible();
    const inputs = page.locator(".modal input");
    expect(await inputs.count()).toBe(2); // api key + domain
    await page.locator(".modal").locator("button", { hasText: "Cancel" }).click();
  });

  test("quota tab shows usage list", async ({ page }) => {
    await page.click('.settings-tab:has-text("quota")');
    await expect(page.locator(".source-list")).toBeVisible();
    await expect(page.locator(".source-row")).toHaveCount(6);
  });
});
