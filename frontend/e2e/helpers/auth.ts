/**
 * E2E auth helper functions.
 */

import type { Page } from "@playwright/test";

let userCounter = 0;

/** Generate a unique test email. */
function uniqueEmail(): string {
  userCounter++;
  return `e2e-user-${Date.now()}-${userCounter}@test.com`;
}

const TEST_PASSWORD = "TestPassword123!";

/** Register a new user and stay on the redirected page. */
export async function registerUser(
  page: Page,
): Promise<{ email: string; password: string }> {
  const email = uniqueEmail();
  await page.goto("/register");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(TEST_PASSWORD);
  await page.getByLabel("Confirm Password").fill(TEST_PASSWORD);
  await page.getByRole("button", { name: "Create Account" }).click();
  await page.waitForURL("**/dashboard");
  return { email, password: TEST_PASSWORD };
}

/** Log in as an existing user. */
export async function loginAs(
  page: Page,
  email: string,
  password: string,
): Promise<void> {
  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign In" }).click();
  await page.waitForURL("**/dashboard");
}
