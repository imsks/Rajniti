import { test, expect } from "@playwright/test"

test.describe("SEO — crawl files", () => {
    test("robots.txt disallows dashboard and points to sitemap", async ({ page }) => {
        const response = await page.goto("/robots.txt")
        expect(response?.status()).toBe(200)
        const body = await response!.text()
        expect(body).toContain("Disallow: /dashboard")
        expect(body).toContain("Sitemap:")
        expect(body).toContain("/sitemap.xml")
    })
})

test.describe("SEO — site-wide structured data", () => {
    test("home page includes WebSite JSON-LD", async ({ page }) => {
        await page.goto("/")
        const jsonLd = page.locator('script[type="application/ld+json"]')
        await expect(jsonLd.first()).toBeAttached({ timeout: 10_000 })
        const content = await jsonLd.first().textContent()
        expect(content).toContain("WebSite")
        expect(content).toContain("SearchAction")
    })
})

test.describe("SEO — public routes load", () => {
    test("/politicians is not redirected to sign-in", async ({ page }) => {
        await page.goto("/politicians")
        await expect(page).not.toHaveURL(/\/auth\/signin/)
    })
})
