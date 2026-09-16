import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"

// Mock next/image
jest.mock("next/image", () => ({
    __esModule: true,
    default: function MockImage({
        alt,
        src,
        onError,
    }: {
        alt: string
        src: string
        onError?: () => void
    }) {
        // eslint-disable-next-line @next/next/no-img-element
        return <img alt={alt} src={src} onError={onError} data-testid="avatar-image" />
    },
}))

import PoliticianAvatar from "@/components/ui/PoliticianAvatar"

describe("PoliticianAvatar", () => {
    it("renders photo when available", () => {
        render(
            <PoliticianAvatar
                name="NARENDRA MODI"
                photo="https://example.com/photo.jpg"
            />,
        )

        const img = screen.getByTestId("avatar-image")
        expect(img).toBeInTheDocument()
        expect(img).toHaveAttribute("src", "https://example.com/photo.jpg")
    })

    it("renders initials when no photo is provided", () => {
        render(<PoliticianAvatar name="NARENDRA MODI" />)

        expect(screen.getByText("NM")).toBeInTheDocument()
    })

    it("renders initials when photo is null", () => {
        render(<PoliticianAvatar name="RAHUL GANDHI" photo={null} />)

        expect(screen.getByText("RG")).toBeInTheDocument()
    })

    it("shows initials fallback on image error", () => {
        render(
            <PoliticianAvatar
                name="NARENDRA MODI"
                photo="https://example.com/broken.jpg"
            />,
        )

        const img = screen.getByTestId("avatar-image")
        fireEvent.error(img)

        // After error, should show initials
        expect(screen.getByText("NM")).toBeInTheDocument()
    })

    it("uses party color for fallback background", () => {
        const { container } = render(
            <PoliticianAvatar name="TEST NAME" party="Bharatiya Janata Party" />,
        )

        const avatar = container.firstChild as HTMLElement
        // BJP color background
        expect(avatar).toHaveStyle({ backgroundColor: "#FAEEDA" })
    })

    it("uses default color when no party is provided", () => {
        const { container } = render(<PoliticianAvatar name="TEST NAME" />)

        const avatar = container.firstChild as HTMLElement
        // Default fallback color
        expect(avatar).toHaveStyle({ backgroundColor: "#F1EFE8" })
    })

    it("respects custom size", () => {
        const { container } = render(
            <PoliticianAvatar name="TEST NAME" size={60} />,
        )

        const avatar = container.firstChild as HTMLElement
        expect(avatar).toHaveStyle({ width: "60px", height: "60px" })
    })

    it("renders question mark for empty name", () => {
        render(<PoliticianAvatar name="" />)

        expect(screen.getByText("?")).toBeInTheDocument()
    })

    it("extracts first two initials from multi-word name", () => {
        render(<PoliticianAvatar name="AMIT SHAH KUMAR" />)

        // Should only show first two words' initials
        expect(screen.getByText("AS")).toBeInTheDocument()
    })

    it("handles single word name", () => {
        render(<PoliticianAvatar name="MODI" />)

        expect(screen.getByText("M")).toBeInTheDocument()
    })
})
