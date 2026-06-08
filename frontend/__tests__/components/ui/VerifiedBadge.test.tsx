import { render, screen } from "@testing-library/react"
import VerifiedBadge from "@/components/VerifiedBadge"

// lucide-react icons need a basic SVG mock in test environments
jest.mock("lucide-react", () => ({
    ShieldCheck: ({ size, ...rest }: { size?: number; [key: string]: unknown }) => (
        <svg data-testid="shield-icon" width={size} {...rest} />
    ),
}))

describe("VerifiedBadge", () => {
    it('shows "Unverified — help us source this" when score is 0', () => {
        render(<VerifiedBadge score={0} />)
        expect(screen.getByText("Unverified — help us source this")).toBeInTheDocument()
    })

    it('shows "Unverified" when score is null', () => {
        render(<VerifiedBadge score={null} />)
        expect(screen.getByText("Unverified — help us source this")).toBeInTheDocument()
    })

    it('shows "Unverified" when score is undefined', () => {
        render(<VerifiedBadge />)
        expect(screen.getByText("Unverified — help us source this")).toBeInTheDocument()
    })

    it("shows rounded percentage for a non-zero score", () => {
        render(<VerifiedBadge score={0.82} />)
        expect(screen.getByText("82% verified")).toBeInTheDocument()
    })

    it("applies green classes for score >= 0.75", () => {
        const { container } = render(<VerifiedBadge score={0.75} />)
        const badge = container.firstChild as HTMLElement
        expect(badge.className).toMatch(/green/)
    })

    it("applies yellow classes for score in [0.60, 0.75)", () => {
        const { container } = render(<VerifiedBadge score={0.65} />)
        const badge = container.firstChild as HTMLElement
        expect(badge.className).toMatch(/yellow/)
    })

    it("applies red classes for score < 0.60 (but > 0)", () => {
        const { container } = render(<VerifiedBadge score={0.4} />)
        const badge = container.firstChild as HTMLElement
        expect(badge.className).toMatch(/red/)
    })

    it("applies red classes for the Unverified state", () => {
        const { container } = render(<VerifiedBadge score={0} />)
        const badge = container.firstChild as HTMLElement
        expect(badge.className).toMatch(/red/)
    })

    it("accepts an extra className", () => {
        const { container } = render(<VerifiedBadge score={0.8} className="mt-2" />)
        const badge = container.firstChild as HTMLElement
        expect(badge.className).toContain("mt-2")
    })
})
