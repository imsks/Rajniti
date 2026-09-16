import { render, screen, fireEvent } from "@testing-library/react"
import SearchTypeaheadOption from "@/components/search/SearchTypeaheadOption"
import { mockMp } from "@/__tests__/helpers/politicianFixtures"

jest.mock("next/image", () => ({
    __esModule: true,
    default: function MockImage(props: { alt: string; src: string }) {
        // eslint-disable-next-line @next/next/no-img-element
        return <img alt={props.alt} src={props.src} />
    },
}))

describe("SearchTypeaheadOption", () => {
    it("renders the politician as a listbox option without a nested button", () => {
        render(
            <ul>
                <SearchTypeaheadOption
                    politician={mockMp}
                    index={0}
                    isHighlighted={false}
                    logoErrors={new Set()}
                    onSelect={jest.fn()}
                    onHighlight={jest.fn()}
                    onLogoError={jest.fn()}
                />
            </ul>,
        )

        const option = screen.getByRole("option")
        expect(option).toHaveTextContent("Narendra Modi")
        expect(option.querySelector("button")).toBeNull()
    })

    it("notifies parent on click and hover", () => {
        const onSelect = jest.fn()
        const onHighlight = jest.fn()

        render(
            <ul>
                <SearchTypeaheadOption
                    politician={mockMp}
                    index={3}
                    isHighlighted={true}
                    logoErrors={new Set()}
                    onSelect={onSelect}
                    onHighlight={onHighlight}
                    onLogoError={jest.fn()}
                />
            </ul>,
        )

        const option = screen.getByRole("option")
        expect(option).toHaveAttribute("aria-selected", "true")

        fireEvent.mouseEnter(option)
        expect(onHighlight).toHaveBeenCalledWith(3)

        fireEvent.click(option)
        expect(onSelect).toHaveBeenCalledWith(mockMp)
    })
})
