import { render, screen } from "@testing-library/react"
import { createRef } from "react"
import SearchTypeaheadDropdown from "@/components/search/SearchTypeaheadDropdown"
import { mockMp } from "@/__tests__/helpers/politicianFixtures"

jest.mock("next/image", () => ({
    __esModule: true,
    default: function MockImage(props: { alt: string; src: string }) {
        // eslint-disable-next-line @next/next/no-img-element
        return <img alt={props.alt} src={props.src} />
    },
}))

const listRef = createRef<HTMLUListElement>()

describe("SearchTypeaheadDropdown", () => {
    it("shows a loading state when there are no results yet", () => {
        render(
            <SearchTypeaheadDropdown
                loading={true}
                error={null}
                results={[]}
                trimmedQuery="modi"
                highlightIndex={-1}
                listRef={listRef}
                logoErrors={new Set()}
                onSelect={jest.fn()}
                onHighlight={jest.fn()}
                onLogoError={jest.fn()}
            />,
        )

        expect(screen.getByText("Searching…")).toBeInTheDocument()
    })

    it("shows an error message", () => {
        render(
            <SearchTypeaheadDropdown
                loading={false}
                error="Search failed"
                results={[]}
                trimmedQuery="modi"
                highlightIndex={-1}
                listRef={listRef}
                logoErrors={new Set()}
                onSelect={jest.fn()}
                onHighlight={jest.fn()}
                onLogoError={jest.fn()}
            />,
        )

        expect(screen.getByText("Search failed")).toBeInTheDocument()
    })

    it("shows an empty state for the query", () => {
        render(
            <SearchTypeaheadDropdown
                loading={false}
                error={null}
                results={[]}
                trimmedQuery="xyz"
                highlightIndex={-1}
                listRef={listRef}
                logoErrors={new Set()}
                onSelect={jest.fn()}
                onHighlight={jest.fn()}
                onLogoError={jest.fn()}
            />,
        )

        expect(screen.getByText(/no matches for/i)).toBeInTheDocument()
        expect(screen.getByText(/xyz/)).toBeInTheDocument()
    })

    it("renders suggestion options", () => {
        render(
            <SearchTypeaheadDropdown
                loading={false}
                error={null}
                results={[mockMp]}
                trimmedQuery="modi"
                highlightIndex={0}
                listRef={listRef}
                logoErrors={new Set()}
                onSelect={jest.fn()}
                onHighlight={jest.fn()}
                onLogoError={jest.fn()}
            />,
        )

        expect(screen.getByRole("option", { name: /narendra modi/i })).toBeInTheDocument()
    })
})
