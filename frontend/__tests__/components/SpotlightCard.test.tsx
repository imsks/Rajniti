import { fireEvent, render, screen } from "@testing-library/react"
import SpotlightCard from "@/components/ui/SpotlightCard"

describe("SpotlightCard", () => {
    it("renders children content", () => {
        render(
            <SpotlightCard>
                <p>Card content</p>
            </SpotlightCard>
        )

        expect(screen.getByText("Card content")).toBeInTheDocument()
    })

    it("updates spotlight position CSS variables on mouse move", () => {
        const { container } = render(
            <SpotlightCard>
                <p>Interactive content</p>
            </SpotlightCard>
        )

        const card = container.firstElementChild as HTMLDivElement
        Object.defineProperty(card, "getBoundingClientRect", {
            value: () =>
                ({
                    left: 100,
                    top: 50,
                    width: 200,
                    height: 100,
                }) as DOMRect,
        })

        fireEvent.mouseMove(card, { clientX: 200, clientY: 100 })

        expect(card.style.getPropertyValue("--spotlight-x")).toBe("50%")
        expect(card.style.getPropertyValue("--spotlight-y")).toBe("50%")
    })
})
