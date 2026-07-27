import { expect, test } from "@playwright/test";

test("core product pages render", async ({ page }) => {
  await page.route("**/api/v1/**", async (route) => {
    const url = route.request().url();
    if (url.includes("/user/profile")) {
      await route.fulfill({
        json: {
          user_id: "usr_e2e",
          display_name: "E2E User",
          email: "e2e@alterlife.io",
          role: "Software Developer",
          level: 3,
          xp: 420,
          next_level_xp: 1000,
          title: "Quest Runner",
          avatar_url: null,
          energy: 90,
          focus: 82,
          max_energy: 100,
          max_focus: 100,
          daily_preferences: {},
        },
      });
      return;
    }
    if (url.includes("/quests/daily")) {
      await route.fulfill({
        json: [
          {
            quest_id: "qst_theory",
            title: "E2E Theory Quest",
            description: "Read a focused resource.",
            xp_reward: 100,
            status: "pending",
            verified_by: "manual",
            time_slot: "Akşam",
            duration_minutes: 20,
          },
        ],
      });
      return;
    }
    if (url.includes("/community/paths")) {
      await route.fulfill({ json: { paths: [], total: 0, members: [], branches: [] } });
      return;
    }
    await route.fulfill({ json: {} });
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "AlterLife" })).toBeVisible();

  await page.goto("/login");
  await expect(page.getByRole("button", { name: /giriş|kayıt|google/i }).first()).toBeVisible();

  await page.evaluate(() => {
    localStorage.setItem("alterlife_token", "mock_token_e2e");
    localStorage.setItem("alterlife_user_id", "usr_e2e");
  });

  await page.goto("/dashboard");
  await expect(page.getByRole("heading", { name: "Daily quests" })).toBeVisible();
  await expect(page.getByText("Gün Akışı")).toBeVisible();

  await page.goto("/simulations");
  await expect(page.getByText("Karar Ağacı")).toBeVisible();

  await page.goto("/community");
  await expect(page.getByText("Rota Radarı")).toBeVisible();
});
