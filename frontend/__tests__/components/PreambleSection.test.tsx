import { render } from "@testing-library/react"
import PreambleSection from "@/components/PreambleSection"

describe("PreambleSection", () => {
    it("renders Ashoka Chakra spokes with fixed precision coordinates", () => {
        const { container } = render(<PreambleSection />)
        const spokes = container.querySelectorAll("line")

        expect(spokes).toHaveLength(24)
        spokes.forEach((spoke) => {
            ;(["x1", "y1", "x2", "y2"] as const).forEach((attr) => {
                const value = spoke.getAttribute(attr)
                expect(value).not.toBeNull()
                expect(Number.isFinite(Number(value))).toBe(true)
                const fractional = value?.split(".")[1] ?? ""
                expect(fractional.length).toBeLessThanOrEqual(4)
            })
        })
    })
})
