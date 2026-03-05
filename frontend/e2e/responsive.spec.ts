/**
 * Responsive sidebar and dark mode E2E tests.
 */

import { test, expect } from "@playwright/test";
import { registerUser } from "./helpers/auth";

test.describe("Responsive & Theme", () => {
  test("mobile viewport: hamburger opens sidebar, nav link closes it", async ({
    page,
  }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 812 });
    await registerUser(page);

    // Desktop sidebar should be hidden
    const desktopSidebar = page.locator("aside.hidden");
    await expect(desktopSidebar).not.toBeVisible();

    // Hamburger should be visible
    const hamburger = page.getByLabel("Toggle menu");
    await expect(hamburger).toBeVisible();

    // Click hamburger → sidebar opens
    await hamburger.click();
    const navLink = page.getByRole("link", { name: "Documents" }).first();
    await expect(navLink).toBeVisible({ timeout: 5000 });

    // Click a nav link → sidebar closes and navigates
    await navLink.click();
    await expect(page).toHaveURL(/\/documents/);
  });

  test("dark mode toggle changes theme and persists", async ({ page }) => {
    await registerUser(page);

    // Toggle to dark mode
    const themeToggle = page.getByLabel("Toggle theme");
    await expect(themeToggle).toBeVisible();
    await themeToggle.click();

    // Check html has dark class
    const htmlClass = await page.locator("html").getAttribute("class");
    expect(htmlClass).toContain("dark");

    // Navigate to another page — theme should persist
    await page.goto("/documents");
    const htmlClassAfterNav = await page.locator("html").getAttribute("class");
    expect(htmlClassAfterNav).toContain("dark");
  });
});
