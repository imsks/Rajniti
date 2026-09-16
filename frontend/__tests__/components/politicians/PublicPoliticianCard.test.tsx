import { render, screen } from "@testing-library/react"
import { mockMp } from "@/__tests__/helpers/politicianFixtures"

jest.mock("next/image", () => ({
  __esModule: true,
  default: function MockImage({
    alt,
    src,
  }: {
    alt: string
    src: string
  }) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img alt={alt} src={src} />
  },
}))

import PublicPoliticianCard from "@/components/politicians/PublicPoliticianCard"

describe("PublicPoliticianCard", () => {
  it("renders a stretched profile link with visible accessible text as a child", () => {
    render(<PublicPoliticianCard politician={mockMp} />)

    const link = screen.getByRole("link", { name: "Narendra Modi" })
    expect(link).toHaveAttribute("href", "/politician/mp-1")
    expect(link.querySelector(".sr-only")).toHaveTextContent("Narendra Modi")
    expect(link.tagName).toBe("A")
  })

  it("sizes the party logo tile with explicit pixel classes", () => {
    const { container } = render(
      <PublicPoliticianCard politician={mockMp} />,
    )

    const tile = container.querySelector(".w-\\[22px\\].h-\\[22px\\]")
    expect(tile).toBeTruthy()
  })

  it("renders a share button that is not nested inside the profile link", () => {
    render(<PublicPoliticianCard politician={mockMp} />)

    const share = screen.getByRole("button", { name: "Share this politician" })
    expect(share.closest("a")).toBeNull()
  })
})
