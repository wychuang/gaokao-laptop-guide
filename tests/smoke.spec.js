const { test, expect } = require("@playwright/test");

test.use({
  channel: "chrome",
  viewport: { width: 1280, height: 900 }
});

test("renders chart, cards, and filters", async ({ page }) => {
  const errors = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });

  await page.goto("http://127.0.0.1:4173/", { waitUntil: "networkidle" });
  await expect(page.getByRole("heading", { name: "高考后游戏本选购可视化" })).toBeVisible();
  await expect(page.locator(".card")).toHaveCount(34);
  await expect(page.locator(".point")).toHaveCount(34);

  await page.getByRole("button", { name: "甜品砖头" }).click();
  await expect(page.locator(".card")).toHaveCount(16);

  await page.locator("#memory-filter").check();
  const filteredCount = await page.locator(".card").count();
  expect(filteredCount).toBeGreaterThan(0);
  expect(filteredCount).toBeLessThan(16);
  expect(errors).toEqual([]);
});
