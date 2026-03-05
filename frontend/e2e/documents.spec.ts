/**
 * Document upload and management E2E tests.
 */

import { test, expect } from "@playwright/test";
import path from "path";
import { registerUser } from "./helpers/auth";

test.describe("Documents", () => {
  test.beforeEach(async ({ page }) => {
    await registerUser(page);
  });

  test("upload a text file as resume and see it in the list", async ({
    page,
  }) => {
    await page.goto("/documents");

    // Select resume type (default) and upload
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(
      path.join(__dirname, "fixtures", "sample.txt"),
    );

    // Wait for success toast
    await expect(page.getByText(/uploaded.*successfully/i)).toBeVisible({
      timeout: 10000,
    });

    // File should appear in the list
    await expect(page.getByText("sample.txt", { exact: true })).toBeVisible();
  });

  test("delete a document removes it from the list", async ({ page }) => {
    await page.goto("/documents");

    // Upload first
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(
      path.join(__dirname, "fixtures", "sample.txt"),
    );
    await expect(page.getByText(/uploaded.*successfully/i)).toBeVisible({
      timeout: 10000,
    });

    // Click delete button
    await page
      .getByRole("button", { name: /delete/i })
      .first()
      .click();

    // Confirm in dialog
    const confirmButton = page.getByRole("button", { name: /confirm|delete/i });
    if (await confirmButton.isVisible()) {
      await confirmButton.click();
    }

    // File should be removed
    await expect(page.getByText("sample.txt", { exact: true })).toBeHidden({
      timeout: 5000,
    });
  });
});
