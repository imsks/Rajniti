"use client"

import {
    useState,
    useEffect,
    useRef,
    useCallback,
    forwardRef,
    useImperativeHandle,
    type KeyboardEvent,
    type ChangeEvent,
    type FormEvent,
} from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { Search, Loader2 } from "lucide-react"
import { useTypeaheadSearch } from "@/hooks/useTypeaheadSearch"
import PoliticianAvatar from "@/components/ui/PoliticianAvatar"
import RoleBadge from "@/components/politicians/RoleBadge"
import {
    getPartyColor,
    getPartyLogo,
    getPartyAcronym,
} from "@/lib/constants/partyColors"
import { toTitleCase, getParty, getPoliticianProfileHref } from "@/lib/politicianUtils"
import type { Politician } from "@/types/politician"

interface SearchTypeaheadProps {
    /** Placeholder text for the input. */
    placeholder?: string
    /** Initial search value. */
    defaultValue?: string
    /** Called when user submits search (Enter with no selection or Search button). */
    onSearch?: (query: string) => void
    /** Called when user navigates to a politician profile. */
    onNavigate?: (politician: Politician) => void
    /** Additional CSS classes for the container. */
    className?: string
    /** Additional CSS classes for the input. */
    inputClassName?: string
    /** Show the Search button. */
    showSearchButton?: boolean
    /** Debounce delay in ms (default: 300). */
    debounceMs?: number
    /** aria-label for the input. */
    ariaLabel?: string
}

export interface SearchTypeaheadRef {
    /** Focus the input. */
    focus: () => void
    /** Get current query value. */
    getValue: () => string
    /** Clear the input and close dropdown. */
    clear: () => void
}

/**
 * Typeahead search component with debounced suggestions.
 * Supports keyboard navigation, click-outside close, and navigation to profiles.
 */
const SearchTypeahead = forwardRef<SearchTypeaheadRef, SearchTypeaheadProps>(
    function SearchTypeahead(
        {
            placeholder = "Search by Name…",
            defaultValue = "",
            onSearch,
            onNavigate,
            className = "",
            inputClassName = "",
            showSearchButton = true,
            debounceMs = 300,
            ariaLabel = "Search politicians by name",
        },
        ref,
    ) {
        const router = useRouter()
        const [query, setQuery] = useState(defaultValue)
        const [isOpen, setIsOpen] = useState(false)
        const [highlightIndex, setHighlightIndex] = useState(-1)
        const [logoErrors, setLogoErrors] = useState<Set<string>>(new Set())

        const inputRef = useRef<HTMLInputElement>(null)
        const containerRef = useRef<HTMLDivElement>(null)
        const listRef = useRef<HTMLUListElement>(null)

        const { results, loading, error, clear: clearSearch } = useTypeaheadSearch(
            query,
            { debounceMs, limit: 8 },
        )

        // Expose imperative handle
        useImperativeHandle(ref, () => ({
            focus: () => inputRef.current?.focus(),
            getValue: () => query,
            clear: () => {
                setQuery("")
                setIsOpen(false)
                setHighlightIndex(-1)
                clearSearch()
            },
        }))

        // Determine if dropdown should be visible
        const trimmedQuery = query.trim()
        const nonSpaceChars = trimmedQuery.replace(/\s/g, "").length
        const showDropdown = isOpen && nonSpaceChars >= 2

        // Close dropdown on click outside
        useEffect(() => {
            if (!showDropdown) return

            function handleClickOutside(e: MouseEvent) {
                if (
                    containerRef.current &&
                    !containerRef.current.contains(e.target as Node)
                ) {
                    setIsOpen(false)
                    setHighlightIndex(-1)
                }
            }

            document.addEventListener("mousedown", handleClickOutside)
            return () => document.removeEventListener("mousedown", handleClickOutside)
        }, [showDropdown])

        // Scroll highlighted item into view
        useEffect(() => {
            if (highlightIndex >= 0 && listRef.current) {
                const item = listRef.current.children[highlightIndex] as HTMLElement
                item?.scrollIntoView({ block: "nearest" })
            }
        }, [highlightIndex])

        // Reset highlight when results change
        useEffect(() => {
            setHighlightIndex(-1)
        }, [results])

        const handleInputChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
            setQuery(e.target.value)
            setIsOpen(true)
            setHighlightIndex(-1)
        }, [])

        const navigateToPolitician = useCallback(
            (politician: Politician) => {
                const href = getPoliticianProfileHref(politician)
                setIsOpen(false)
                setHighlightIndex(-1)
                onNavigate?.(politician)
                router.push(href)
            },
            [router, onNavigate],
        )

        const handleSubmit = useCallback(
            (e?: FormEvent) => {
                e?.preventDefault()

                // If a row is highlighted, navigate to that profile
                if (highlightIndex >= 0 && results[highlightIndex]) {
                    navigateToPolitician(results[highlightIndex])
                    return
                }

                // Otherwise, run the full search
                setIsOpen(false)
                setHighlightIndex(-1)
                onSearch?.(query.trim())
            },
            [highlightIndex, results, query, onSearch, navigateToPolitician],
        )

        const handleKeyDown = useCallback(
            (e: KeyboardEvent<HTMLInputElement>) => {
                if (!showDropdown || results.length === 0) {
                    // Let Enter trigger form submit even without dropdown
                    if (e.key === "Enter") {
                        e.preventDefault()
                        handleSubmit()
                    }
                    return
                }

                switch (e.key) {
                    case "ArrowDown":
                        e.preventDefault()
                        setHighlightIndex((prev) =>
                            prev < results.length - 1 ? prev + 1 : prev,
                        )
                        break
                    case "ArrowUp":
                        e.preventDefault()
                        setHighlightIndex((prev) => (prev > 0 ? prev - 1 : -1))
                        break
                    case "Enter":
                        e.preventDefault()
                        handleSubmit()
                        break
                    case "Escape":
                        e.preventDefault()
                        setIsOpen(false)
                        setHighlightIndex(-1)
                        break
                }
            },
            [showDropdown, results.length, handleSubmit],
        )

        const handleInputFocus = useCallback(() => {
            const nonSpaceChars = query.trim().replace(/\s/g, "").length
            if (nonSpaceChars >= 2) {
                setIsOpen(true)
            }
        }, [query])

        // Handle native search clear (×)
        useEffect(() => {
            const el = inputRef.current
            if (!el) return

            function onNativeSearch() {
                if (el!.value === "") {
                    setQuery("")
                    setIsOpen(false)
                    setHighlightIndex(-1)
                    clearSearch()
                }
            }

            el.addEventListener("search", onNativeSearch)
            return () => el.removeEventListener("search", onNativeSearch)
        }, [clearSearch])

        const handleLogoError = useCallback((partyKey: string) => {
            setLogoErrors((prev) => new Set(prev).add(partyKey))
        }, [])

        return (
            <div ref={containerRef} className={`relative ${className}`}>
                <form
                    onSubmit={handleSubmit}
                    className="flex items-center gap-3"
                    role="search"
                >
                    <div className="relative flex-1">
                        <Search
                            size={16}
                            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                            aria-hidden="true"
                        />
                        <input
                            ref={inputRef}
                            type="search"
                            value={query}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            onFocus={handleInputFocus}
                            placeholder={placeholder}
                            aria-label={ariaLabel}
                            aria-expanded={showDropdown}
                            aria-controls="search-typeahead-listbox"
                            aria-activedescendant={
                                highlightIndex >= 0
                                    ? `search-typeahead-option-${highlightIndex}`
                                    : undefined
                            }
                            role="combobox"
                            aria-autocomplete="list"
                            autoComplete="off"
                            className={`w-full h-12 pl-9 pr-4 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-orange-300 dark:focus:ring-orange-600 ${inputClassName}`}
                        />
                        {loading && (
                            <Loader2
                                size={16}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 animate-spin"
                                aria-hidden="true"
                            />
                        )}
                    </div>
                    {showSearchButton && (
                        <button
                            type="submit"
                            className="shrink-0 h-12 px-6 rounded-lg bg-orange-600/90 hover:bg-orange-600 text-white text-sm font-semibold transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-orange-300 dark:focus:ring-orange-600"
                        >
                            Search
                        </button>
                    )}
                </form>

                {/* Dropdown */}
                {showDropdown && (
                    <div
                        id="search-typeahead-listbox"
                        role="listbox"
                        className="absolute z-30 left-0 right-0 top-full mt-1.5 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 shadow-lg max-h-[400px] overflow-auto"
                    >
                        {loading && results.length === 0 ? (
                            <div className="px-4 py-6 text-center text-gray-500 dark:text-gray-400 text-sm flex items-center justify-center gap-2">
                                <Loader2
                                    size={16}
                                    className="animate-spin"
                                    aria-hidden="true"
                                />
                                Searching…
                            </div>
                        ) : error ? (
                            <div className="px-4 py-3 text-sm text-red-600 dark:text-red-400">
                                {error}
                            </div>
                        ) : results.length === 0 ? (
                            <div className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                                No matches for &ldquo;{trimmedQuery}&rdquo;
                            </div>
                        ) : (
                            <ul ref={listRef} className="py-1">
                                {results.map((politician, index) => {
                                    const party = getParty(politician)
                                    const partyDisplay = party !== "—" ? party : null
                                    const partyColor = getPartyColor(partyDisplay)
                                    const partyLogo = getPartyLogo(partyDisplay)
                                    const partyKey = partyDisplay || ""
                                    const showLogo = partyLogo && !logoErrors.has(partyKey)

                                    const isHighlighted = index === highlightIndex

                                    return (
                                        <li
                                            key={`${politician.id}-${politician.type}`}
                                            id={`search-typeahead-option-${index}`}
                                            role="option"
                                            aria-selected={isHighlighted}
                                        >
                                            <button
                                                type="button"
                                                onClick={() => navigateToPolitician(politician)}
                                                onMouseEnter={() => setHighlightIndex(index)}
                                                className={`w-full px-4 py-2.5 flex items-center gap-3 text-left transition-colors cursor-pointer ${
                                                    isHighlighted
                                                        ? "bg-orange-50 dark:bg-gray-800"
                                                        : "hover:bg-gray-50 dark:hover:bg-gray-800"
                                                }`}
                                            >
                                                {/* Left: Avatar + Name + Badge */}
                                                <div className="flex items-center gap-3 flex-1 min-w-0">
                                                    <PoliticianAvatar
                                                        photo={politician.photo}
                                                        name={politician.name}
                                                        party={partyDisplay}
                                                        size={36}
                                                    />
                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex items-center gap-2">
                                                            <span className="font-medium text-gray-900 dark:text-white truncate">
                                                                {toTitleCase(politician.name)}
                                                            </span>
                                                            <RoleBadge type={politician.type} />
                                                        </div>
                                                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                                                            {toTitleCase(politician.constituency)},{" "}
                                                            {politician.state}
                                                        </p>
                                                    </div>
                                                </div>

                                                {/* Right: Party logo or colored dot */}
                                                <div className="shrink-0 flex items-center justify-center w-6 h-6">
                                                    {showLogo ? (
                                                        <span className="relative w-5 h-5">
                                                            <Image
                                                                src={partyLogo}
                                                                alt={getPartyAcronym(partyDisplay) || ""}
                                                                fill
                                                                className="object-contain"
                                                                sizes="20px"
                                                                onError={() =>
                                                                    handleLogoError(partyKey)
                                                                }
                                                            />
                                                        </span>
                                                    ) : (
                                                        <span
                                                            className="w-3 h-3 rounded-full"
                                                            style={{
                                                                backgroundColor: partyColor.text,
                                                            }}
                                                            aria-label={
                                                                partyDisplay
                                                                    ? getPartyAcronym(partyDisplay)
                                                                    : "Independent"
                                                            }
                                                        />
                                                    )}
                                                </div>
                                            </button>
                                        </li>
                                    )
                                })}
                            </ul>
                        )}
                    </div>
                )}
            </div>
        )
    },
)

export default SearchTypeahead
