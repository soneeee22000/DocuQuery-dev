/**
 * Auth E2E tests: register, login, guards, logout.
 */

import { test, expect } from "@playwright/test";
import { registerUser } from "./helpers/auth";

test.describe("Authentication", () => {
  test("register redirects to dashboard", async ({ page }) => {
    const { email } = await registerUser(page);
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByText(email)).toBeVisible();
  });

  test("login with wrong password shows error", async ({ page }) => {
    const { email } = await registerUser(page);

    // Logout first
    await page.getByRole("button", { name: "Sign Out" }).click();
    await expect(page).toHaveURL(/\/login/);

    // Try wrong password
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password").fill("WrongPassword999!");
    await page.getByRole("button", { name: "Sign In" }).click();

    await expect(page.getByText(/invalid|incorrect|failed/i)).toBeVisible({
      timeout: 5000,
    });
  });

  test("unauthenticated user is redirected to login", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });

  test("logout redirects to login", async ({ page }) => {
    await registerUser(page);
    await page.getByRole("button", { name: "Sign Out" }).click();
    await expect(page).toHaveURL(/\/login/);
  });
});
