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

    expect(
      screen.getByRole("link", { name: "Go to previous page" }),
    ).toHaveAttribute(
      "href",
      "/politicians/mp",
    )
    expect(screen.getByRole("link", { name: "Go to next page" })).toHaveAttribute(
      "href",
      "/politicians/mp/page/3",
    )
    expect(screen.getAllByLabelText("Page 2, current page")).toHaveLength(2)
  })

  it("omits the previous link on the first page", () => {
    render(
      <PoliticiansPagination page={1} totalPages={3} filters={{}} />,
    )

    expect(
      screen.queryByRole("link", { name: "Go to previous page" }),
    ).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Go to next page" })).toHaveAttribute(
      "href",
      "/politicians/page/2",
    )
  })
})
