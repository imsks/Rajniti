import { render, screen } from "@testing-library/react"
import Footer from "@/components/layout/Footer"

describe("Footer", () => {
    it("renders compact one-line content with github link", () => {
        render(<Footer />)

        expect(screen.getByText(/Building with ❤️ for 🇮🇳 Democracy/i)).toBeVisible()
        expect(
            screen.getByText(new RegExp(`© ${new Date().getFullYear()} Rajniti`, "i"))
        ).toBeVisible()
        expect(screen.getByRole("link", { name: /github/i })).toHaveAttribute(
            "href",
            "https://github.com/imsks/rajniti"
        )
    })
})
