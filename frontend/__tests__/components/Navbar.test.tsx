import { fireEvent, render, screen, within } from "@testing-library/react"
import Navbar from "@/components/layout/Navbar"

describe("Navbar", () => {
    it("renders scrollable primary navigation links for the default variant", () => {
        render(<Navbar variant='default' />)

        const nav = screen.getByRole("navigation", { name: /primary navigation/i })
        expect(nav.firstElementChild).toHaveClass("overflow-x-auto")

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

    it("toggles mobile burger menu and renders mobile links", () => {
        render(<Navbar variant='default' />)

        const toggle = screen.getByRole("button", { name: /open menu/i })
        fireEvent.click(toggle)

        const mobileNav = screen.getByRole("navigation", { name: /mobile navigation/i })
        expect(within(mobileNav).getByRole("link", { name: /explore politicians/i })).toHaveAttribute(
            "href",
            "/dashboard"
        )

        fireEvent.click(screen.getByRole("button", { name: /close menu/i }))
        expect(screen.queryByRole("navigation", { name: /mobile navigation/i })).not.toBeInTheDocument()
    })

    it("closes mobile menu when resizing to desktop viewport", () => {
        render(<Navbar variant='default' />)

        fireEvent.click(screen.getByRole("button", { name: /open menu/i }))
        expect(screen.getByRole("navigation", { name: /mobile navigation/i })).toBeInTheDocument()

        Object.defineProperty(window, "innerWidth", { configurable: true, writable: true, value: 1024 })
        fireEvent(window, new Event("resize"))

        expect(screen.queryByRole("navigation", { name: /mobile navigation/i })).not.toBeInTheDocument()
    })
})
