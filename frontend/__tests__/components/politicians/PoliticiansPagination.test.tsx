import { render, screen } from "@testing-library/react"
import { PoliticiansPagination } from "@/components/politicians/PoliticiansDirectory"

describe("PoliticiansPagination", () => {
  it("renders nothing when there is only one page", () => {
    const { container } = render(
      <PoliticiansPagination page={1} totalPages={1} filters={{}} />,
    )
    expect(container).toBeEmptyDOMElement()
  })

  it("links to previous and next pages", () => {
    render(
      <PoliticiansPagination
        page={2}
        totalPages={4}
        filters={{ type: "MP" }}
      />,
    )

    expect(screen.getByRole("link", { name: "Previous" })).toHaveAttribute(
      "href",
      "/politicians/mp",
    )
    expect(screen.getByRole("link", { name: "Next" })).toHaveAttribute(
      "href",
      "/politicians/mp/page/3",
    )
    expect(screen.getByText("Page 2 of 4")).toBeInTheDocument()
  })

  it("omits the previous link on the first page", () => {
    render(
      <PoliticiansPagination page={1} totalPages={3} filters={{}} />,
    )

    expect(screen.queryByRole("link", { name: "Previous" })).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Next" })).toHaveAttribute(
      "href",
      "/politicians/page/2",
    )
  })
})
