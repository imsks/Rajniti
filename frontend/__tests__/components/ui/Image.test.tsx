import { render, screen } from "@testing-library/react"
import Image from "@/components/ui/Image"

jest.mock("next/image", () => {
    return function MockNextImage({
        src,
        alt,
        unoptimized,
        loading,
        priority,
        sizes,
        ...rest
    }: {
        src: string
        alt: string
        unoptimized?: boolean
        loading?: string
        priority?: boolean
        sizes?: string
        width?: number
        height?: number
        className?: string
    }) {
        return (
            <img
                src={typeof src === "string" ? src : ""}
                alt={alt}
                data-unoptimized={String(unoptimized ?? false)}
                data-loading={loading ?? ""}
                data-priority={String(priority ?? false)}
                data-sizes={sizes ?? ""}
                {...rest}
            />
        )
    }
})

describe("Image", () => {
    it("optimizes allowlisted ECI external URLs", () => {
        render(
            <Image
                src="https://results.eci.gov.in/uploads4/candprofile/photo.jpg"
                alt="Politician"
                width={128}
                height={128}
            />
        )

        const img = screen.getByRole("img", { name: "Politician" })
        expect(img).toHaveAttribute("data-unoptimized", "false")
    })

    it("leaves unknown external URLs unoptimized", () => {
        render(
            <Image
                src="https://cdn.example.com/photo.jpg"
                alt="External"
                width={56}
                height={56}
            />
        )

        const img = screen.getByRole("img", { name: "External" })
        expect(img).toHaveAttribute("data-unoptimized", "true")
    })

    it("uses priority without lazy loading for LCP images", () => {
        render(
            <Image
                src="https://results.eci.gov.in/photo.jpg"
                alt="Hero"
                width={128}
                height={128}
                priority
                sizes="128px"
            />
        )

        const img = screen.getByRole("img", { name: "Hero" })
        expect(img).toHaveAttribute("data-priority", "true")
        expect(img).toHaveAttribute("data-loading", "")
        expect(img).toHaveAttribute("data-sizes", "128px")
    })

    it("defaults to lazy loading when priority is not set", () => {
        render(
            <Image
                src="/default-avatar.png"
                alt="Local"
                width={56}
                height={56}
            />
        )

        const img = screen.getByRole("img", { name: "Local" })
        expect(img).toHaveAttribute("data-loading", "lazy")
    })
})
