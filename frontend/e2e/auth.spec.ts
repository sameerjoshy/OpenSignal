import { test, expect } from "@playwright/test";

// A unique email per run so the test can re-signup without collisions.
const TS = Date.now();
const EMAIL = `e2e-${TS}@example.com`;
const PASSWORD = "password123";
const NAME = "E2E Tester";

test.describe("Auth flows", () => {
  test("signup creates an account and lands on onboarding", async ({ page }) => {
    await page.goto("/signup");

    await expect(page.locator(".auth-title")).toContainText("Create your account");

    await page.fill("#fullName", NAME);
    await page.fill("#email", EMAIL);
    await page.fill("#password", PASSWORD);
    await page.click('button[type="submit"]:has-text("Create account")');

    // Should reach onboarding (workspace step)
    await expect(page).toHaveURL(/\/onboarding/, { timeout: 15000 });
    await expect(page.locator("h2", { hasText: "Welcome" })).toBeVisible();
  });

  test("signup shows error for short password", async ({ page }) => {
    await page.goto("/signup");
    await page.fill("#fullName", "Test User");
    await page.fill("#email", `bad-${TS}@example.com`);
    await page.fill("#password", "short");
    // HTML5 minLength blocks submission; ensure we stay on the page
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/signup/);
  });

  test("login works and reaches dashboard", async ({ page }) => {
    // Mark onboarding complete so a logged-in user lands on the dashboard
    await page.addInitScript(() => localStorage.setItem("onboarding_done", "1"));
    await page.goto("/login");
    await expect(page.locator(".auth-title")).toContainText("Welcome back");

    await page.fill("#email", EMAIL);
    await page.fill("#password", PASSWORD);
    await page.click('button[type="submit"]:has-text("Sign in")');

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 15000 });
    await expect(page.locator(".page-title", { hasText: "Dashboard" })).toBeVisible();
  });

  test("login rejects wrong password with an error", async ({ page }) => {
    await page.goto("/login");
    await page.fill("#email", EMAIL);
    await page.fill("#password", "wrongpassword");
    await page.click('button[type="submit"]:has-text("Sign in")');

    await expect(page.locator(".alert-error")).toBeVisible();
  });

  test("logout returns to landing", async ({ page }) => {
    await page.addInitScript(() => localStorage.setItem("onboarding_done", "1"));
    // Login first
    await page.goto("/login");
    await page.fill("#email", EMAIL);
    await page.fill("#password", PASSWORD);
    await page.click('button[type="submit"]:has-text("Sign in")');
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 15000 });

    // Sign out via sidebar
    await page.click('button[title="Sign out"]');
    await expect(page).toHaveURL(/\/login/, { timeout: 15000 });
    await expect(page.locator(".auth-title", { hasText: "Welcome back" })).toBeVisible();
  });
});
