import React from "react"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = jest.fn()

// Mock the router
const mockPush = jest.fn()
jest.mock("next/navigation", () => ({
    useRouter: () => ({
        push: mockPush,
    }),
}))

// Mock next/image
jest.mock("next/image", () => ({
    __esModule: true,
    default: function MockImage(props: { alt: string; src: string }) {
        // eslint-disable-next-line @next/next/no-img-element
        return <img alt={props.alt} src={props.src} />
    },
}))

// Mock the useTypeaheadSearch hook
const mockUseTypeaheadSearch = jest.fn()
jest.mock("@/hooks/useTypeaheadSearch", () => ({
    useTypeaheadSearch: (...args: unknown[]) => mockUseTypeaheadSearch(...args),
}))

// Import after mocking
import SearchTypeahead from "@/components/search/SearchTypeahead"

describe("SearchTypeahead", () => {
    const mockPoliticians = [
        {
            id: "1",
            name: "NARENDRA MODI",
            type: "MP" as const,
            slug: "narendra-modi",
            photo: "https://example.com/photo.jpg",
            state: "Gujarat",
            constituency: "Varanasi",
            political_background: {
                elections: [{ party: "Bharatiya Janata Party" }],
            },
        },
        {
            id: "2",
            name: "RAHUL GANDHI",
            type: "MP" as const,
            slug: "rahul-gandhi",
            photo: null,
            state: "Kerala",
            constituency: "Wayanad",
            political_background: {
                elections: [{ party: "Indian National Congress" }],
            },
        },
    ]

    beforeEach(() => {
        mockPush.mockClear()
        mockUseTypeaheadSearch.mockReset()
        mockUseTypeaheadSearch.mockReturnValue({
            results: [],
            loading: false,
            error: null,
            clear: jest.fn(),
        })
    })

    it("renders input with placeholder", () => {
        render(<SearchTypeahead placeholder="Search here..." />)
        expect(screen.getByPlaceholderText("Search here...")).toBeInTheDocument()
    })

    it("renders search button when showSearchButton is true", () => {
        render(<SearchTypeahead showSearchButton={true} />)
        expect(screen.getByRole("button", { name: /search/i })).toBeInTheDocument()
    })

    it("does not render search button when showSearchButton is false", () => {
        render(<SearchTypeahead showSearchButton={false} />)
        expect(
            screen.queryByRole("button", { name: /search/i }),
        ).not.toBeInTheDocument()
    })

    it("calls onSearch when form is submitted with no highlighted row", () => {
        const onSearch = jest.fn()
        render(<SearchTypeahead onSearch={onSearch} />)

        const input = screen.getByRole("combobox")
        fireEvent.change(input, { target: { value: "modi" } })
        fireEvent.keyDown(input, { key: "Enter", code: "Enter" })

        expect(onSearch).toHaveBeenCalledWith("modi")
    })

    it("shows dropdown with results when there are matches", () => {
        mockUseTypeaheadSearch.mockReturnValue({
            results: mockPoliticians,
            loading: false,
            error: null,
            clear: jest.fn(),
        })

        render(<SearchTypeahead />)

        const input = screen.getByRole("combobox")
        fireEvent.change(input, { target: { value: "modi" } })
        fireEvent.focus(input)

        // Dropdown should appear
        expect(screen.getByRole("listbox")).toBeInTheDocument()
        expect(screen.getByText("Narendra Modi")).toBeInTheDocument()
        expect(screen.getByText("Rahul Gandhi")).toBeInTheDocument()
    })

    it("shows loading state", () => {
        mockUseTypeaheadSearch.mockReturnValue({
            results: [],
            loading: true,
            error: null,
            clear: jest.fn(),
        })

        render(<SearchTypeahead />)

        const input = screen.getByRole("combobox")
        fireEvent.change(input, { target: { value: "modi" } })

        expect(screen.getByText("Searching…")).toBeInTheDocument()
    })

    it("shows error state", () => {
        mockUseTypeaheadSearch.mockReturnValue({
            results: [],
            loading: false,
            error: "Search failed",
            clear: jest.fn(),
        })

        render(<SearchTypeahead />)

        const input = screen.getByRole("combobox")
        fireEvent.change(input, { target: { value: "modi" } })

        expect(screen.getByText("Search failed")).toBeInTheDocument()
    })

    it("shows empty state", () => {
        mockUseTypeaheadSearch.mockReturnValue({
            results: [],
            loading: false,
            error: null,
            clear: jest.fn(),
        })

        render(<SearchTypeahead />)

        const input = screen.getByRole("combobox")
        fireEvent.change(input, { target: { value: "xyz" } })

        expect(screen.getByText(/no matches for/i)).toBeInTheDocument()
    })

    it("navigates to politician profile on click", () => {
        mockUseTypeaheadSearch.mockReturnValue({
            results: mockPoliticians,
            loading: false,
            error: null,
            clear: jest.fn(),
        })

        render(<SearchTypeahead />)

        const input = screen.getByRole("combobox")
        fireEvent.change(input, { target: { value: "modi" } })

        const option = screen.getByText("Narendra Modi")
        fireEvent.click(option)

        expect(mockPush).toHaveBeenCalledWith("/politician/narendra-modi")
    })

    it("highlights row on arrow down and navigates on enter", () => {
        mockUseTypeaheadSearch.mockReturnValue({
            results: mockPoliticians,
            loading: false,
            error: null,
            clear: jest.fn(),
        })

        render(<SearchTypeahead />)

        const input = screen.getByRole("combobox")
        fireEvent.change(input, { target: { value: "modi" } })

        // Press arrow down to highlight first item
        fireEvent.keyDown(input, { key: "ArrowDown", code: "ArrowDown" })

        // Press enter to navigate
        fireEvent.keyDown(input, { key: "Enter", code: "Enter" })

        expect(mockPush).toHaveBeenCalledWith("/politician/narendra-modi")
    })

    it("closes dropdown on escape", () => {
        mockUseTypeaheadSearch.mockReturnValue({
            results: mockPoliticians,
            loading: false,
            error: null,
            clear: jest.fn(),
        })

        render(<SearchTypeahead />)

        const input = screen.getByRole("combobox")
        fireEvent.change(input, { target: { value: "modi" } })

        // Dropdown should be open
        expect(screen.getByRole("listbox")).toBeInTheDocument()

        // Press escape
        fireEvent.keyDown(input, { key: "Escape", code: "Escape" })

        // Dropdown should be closed
        expect(screen.queryByRole("listbox")).not.toBeInTheDocument()
    })

    it("does not show dropdown for short queries", () => {
        mockUseTypeaheadSearch.mockReturnValue({
            results: [],
            loading: false,
            error: null,
            clear: jest.fn(),
        })

        render(<SearchTypeahead />)

        const input = screen.getByRole("combobox")
        fireEvent.change(input, { target: { value: "m" } })

        expect(screen.queryByRole("listbox")).not.toBeInTheDocument()
    })

    it("displays MP/MLA badge correctly", () => {
        mockUseTypeaheadSearch.mockReturnValue({
            results: mockPoliticians,
            loading: false,
            error: null,
            clear: jest.fn(),
        })

        render(<SearchTypeahead />)

        const input = screen.getByRole("combobox")
        fireEvent.change(input, { target: { value: "modi" } })

        // Should show MP badges
        expect(screen.getAllByText("MP")).toHaveLength(2)
    })

    it("uses defaultValue prop", () => {
        render(<SearchTypeahead defaultValue="initial search" />)

        const input = screen.getByRole("combobox")
        expect(input).toHaveValue("initial search")
    })

    it("calls onNavigate when navigating to a politician", () => {
        const onNavigate = jest.fn()
        mockUseTypeaheadSearch.mockReturnValue({
            results: mockPoliticians,
            loading: false,
            error: null,
            clear: jest.fn(),
        })

        render(<SearchTypeahead onNavigate={onNavigate} />)

        const input = screen.getByRole("combobox")
        fireEvent.change(input, { target: { value: "modi" } })

        const option = screen.getByText("Narendra Modi")
        fireEvent.click(option)

        expect(onNavigate).toHaveBeenCalledWith(mockPoliticians[0])
    })
})
