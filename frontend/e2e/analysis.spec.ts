/**
 * Analysis E2E tests with mocked LLM responses.
 */

import { test, expect } from "@playwright/test";
import path from "path";
import { registerUser } from "./helpers/auth";

const MOCK_ANALYSIS_RESPONSE = {
  data: {
    id: "mock-analysis-id",
    resume_id: "r1",
    jd_id: "j1",
    resume_name: "sample.txt",
    jd_name: "jd.txt",
    score: 75,
    results: {
      score: 75,
      categories: {
        skills: {
          score: 80,
          matched: ["Python", "React"],
          missing: ["Kubernetes"],
          feedback: "Strong skills match.",
        },
        experience: {
          score: 70,
          matched: ["5 years"],
          missing: ["Team lead"],
          feedback: "Good experience.",
        },
        education: {
          score: 85,
          matched: ["CS degree"],
          missing: [],
          feedback: "Education matches well.",
        },
        keywords: {
          score: 65,
          matched: ["API", "microservices"],
          missing: ["CI/CD"],
          feedback: "Some keyword gaps.",
        },
      },
      keyword_gaps: ["Kubernetes", "CI/CD"],
    },
    tips: [
      {
        priority: 1,
        category: "skills",
        suggestion: "Add Kubernetes experience",
        section: "Skills",
      },
    ],
    llm_model: "gpt-4o-mini",
    created_at: new Date().toISOString(),
  },
  error: null,
  meta: {},
};

/** Upload a sample file as the given doc type. */
async function uploadFile(
  page: import("@playwright/test").Page,
  docType: "resume" | "job_description",
) {
  await page.goto("/documents");

  if (docType === "job_description") {
    await page.getByRole("button", { name: "Job Description" }).click();
  }

  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(path.join(__dirname, "fixtures", "sample.txt"));
  await expect(page.getByText(/uploaded.*successfully/i)).toBeVisible({
    timeout: 10000,
  });
}

test.describe("Analysis", () => {
  test("new analysis with doc selection shows results", async ({ page }) => {
    await registerUser(page);

    // Upload resume and JD
    await uploadFile(page, "resume");
    await uploadFile(page, "job_description");

    // Mock the analysis API
    await page.route("**/api/v1/analysis/match", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_ANALYSIS_RESPONSE),
      });
    });

    // Mock the get analysis endpoint
    await page.route("**/api/v1/analysis/mock-analysis-id", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_ANALYSIS_RESPONSE),
      });
    });

    // Go to new analysis
    await page.goto("/analysis/new");

    // Select resume and JD
    await page.getByText("Select a resume").click();
    await page.getByRole("option").first().click();

    await page.getByText("Select a job description").click();
    await page.getByRole("option").first().click();

    // Trigger analysis
    await page.getByRole("button", { name: "Analyze Match" }).click();

    // Should navigate to results
    await expect(page).toHaveURL(/\/analysis\/mock-analysis-id/, {
      timeout: 10000,
    });

    // Score gauge and categories should be visible
    await expect(page.getByText("75")).toBeVisible();
    await expect(page.getByText("Skills")).toBeVisible();
    await expect(page.getByText("Experience")).toBeVisible();
  });

  test("analysis result page shows score, categories, and tips", async ({
    page,
  }) => {
    await registerUser(page);

    // Mock the get analysis endpoint
    await page.route("**/api/v1/analysis/mock-analysis-id", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_ANALYSIS_RESPONSE),
      });
    });

    await page.goto("/analysis/mock-analysis-id");

    // Score gauge
    await expect(page.getByText("75")).toBeVisible({ timeout: 5000 });
    await expect(page.getByText("Match Score")).toBeVisible();

    // Category cards
    await expect(page.getByText("Skills")).toBeVisible();
    await expect(page.getByText("Experience")).toBeVisible();
    await expect(page.getByText("Education")).toBeVisible();
    await expect(page.getByText("Keywords")).toBeVisible();

    // Tips
    await expect(page.getByText("Add Kubernetes experience")).toBeVisible();
  });
});
