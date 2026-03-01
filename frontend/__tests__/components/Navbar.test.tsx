import { render, screen, within } from "@testing-library/react"
import Navbar from "@/components/layout/Navbar"

describe("Navbar", () => {
    it("renders scrollable primary navigation links for the default variant", () => {
        render(<Navbar variant='default' />)

        const nav = screen.getByRole("navigation", { name: /primary navigation/i })
        expect(nav.firstChild).toHaveClass("overflow-x-auto")

        expect(within(nav).getByRole("link", { name: /explore politicians/i })).toHaveAttribute(
            "href",
            "/dashboard"
        )
        expect(within(nav).getByRole("link", { name: /about/i })).toHaveAttribute(
            "href",
            "#about"
        )
        expect(within(nav).getByRole("link", { name: /contribute/i })).toHaveAttribute(
            "href",
            "#contribute"
        )
        expect(within(nav).getByRole("link", { name: /join community/i })).toHaveAttribute(
            "href",
            "https://chat.whatsapp.com/IceA98FSHHuDmXOwv8WH7v"
        )
    })

    it("renders dashboard navigation links including bug report", () => {
        render(<Navbar variant='dashboard' />)

        const nav = screen.getByRole("navigation", { name: /primary navigation/i })
        expect(within(nav).getByRole("link", { name: /home/i })).toBeVisible()
        expect(within(nav).getByRole("link", { name: /politicians/i })).toBeVisible()
        expect(within(nav).getByRole("link", { name: /found a bug/i })).toHaveAttribute(
            "href",
            "https://github.com/imsks/rajniti/issues/new"
        )
    })
})
