import { render, screen } from "@testing-library/react"
import Button from "@/components/ui/Button"

describe("Button", () => {
    it("does not forward icon props to the DOM for link buttons", () => {
        render(
            <Button href='/dashboard' leftIcon={<span>L</span>} rightIcon={<span>R</span>}>
                Explore
            </Button>
        )

        const link = screen.getByRole("link", { name: /explore/i })
        expect(link).not.toHaveAttribute("lefticon")
        expect(link).not.toHaveAttribute("righticon")
    })
})
