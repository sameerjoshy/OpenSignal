import { test, expect } from "@playwright/test";

const PASSWORD = "password123";

test.describe("Dashboard & app shell", () => {
  test.beforeEach(async ({ page }) => {
    const email = `e2e-dash-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.com`;
    // Mark onboarding complete so the signed-up user can reach the dashboard
    await page.addInitScript(() => localStorage.setItem("onboarding_done", "1"));
    // Create + log in a fresh user
    await page.goto("/signup");
    await page.fill("#fullName", "Dash User");
    await page.fill("#email", email);
    await page.fill("#password", PASSWORD);
    await page.click('button[type="submit"]:has-text("Create account")');
    // onboarding_done is set via init script, so signup redirects straight to the dashboard
    await expect(page.locator(".page-title", { hasText: "Dashboard" })).toBeVisible();
  });

  test("dashboard shows metrics and performance hero", async ({ page }) => {
    await expect(page.locator(".perf-hero")).toBeVisible();
    // 5 primary metric cards + 4 outcomes metric cards
    await expect(page.locator(".metric-card")).toHaveCount(9);
  });

  test("sidebar navigation reaches each section", async ({ page }) => {
    const links = [
      { label: "Signals", url: /\/signals/ },
      { label: "Accounts", url: /\/accounts/ },
      { label: "Campaigns", url: /\/campaigns/ },
      { label: "Analytics", url: /\/analytics/ },
      { label: "Outcomes", url: /\/outcomes/ },
      { label: "Learning", url: /\/learning/ },
      { label: "Settings", url: /\/settings/ },
    ];
    for (const link of links) {
      await page.click(`.nav-link:has-text("${link.label}")`);
      await expect(page).toHaveURL(link.url, { timeout: 10000 });
    }
  });

  test("theme toggle switches to dark mode", async ({ page }) => {
    const html = page.locator("html");
    const before = await html.getAttribute("data-theme");
    await page.click(".theme-toggle");
    await expect(html).toHaveAttribute("data-theme", before === "dark" ? "light" : "dark");
  });

  test("new campaign button in topbar opens builder", async ({ page }) => {
    await page.click('.topbar button:has-text("New campaign")');
    await expect(page).toHaveURL(/\/campaigns\/new/);
  });

  test("command palette opens with Ctrl+K", async ({ page }) => {
    await page.keyboard.press("Control+k");
    await expect(page.locator(".cmd-palette")).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.locator(".cmd-palette")).not.toBeVisible();
  });
});
