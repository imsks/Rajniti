"use client"

import { type RefObject } from "react"
import { Loader2 } from "lucide-react"
import SearchTypeaheadOption from "@/components/search/SearchTypeaheadOption"
import type { Politician } from "@/types/politician"

interface SearchTypeaheadDropdownProps {
    loading: boolean
    error: string | null
    results: Politician[]
    trimmedQuery: string
    highlightIndex: number
    listRef: RefObject<HTMLUListElement | null>
    logoErrors: Set<string>
    onSelect: (politician: Politician) => void
    onHighlight: (index: number) => void
    onLogoError: (partyKey: string) => void
}

/**
 * Typeahead results panel: loading, error, empty, and suggestion list states.
 */
export default function SearchTypeaheadDropdown({
    loading,
    error,
    results,
    trimmedQuery,
    highlightIndex,
    listRef,
    logoErrors,
    onSelect,
    onHighlight,
    onLogoError,
}: SearchTypeaheadDropdownProps) {
    return (
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
                    {results.map((politician, index) => (
                        <SearchTypeaheadOption
                            key={`${politician.id}-${politician.type}`}
                            politician={politician}
                            index={index}
                            isHighlighted={index === highlightIndex}
                            logoErrors={logoErrors}
                            onSelect={onSelect}
                            onHighlight={onHighlight}
                            onLogoError={onLogoError}
                        />
                    ))}
                </ul>
            )}
        </div>
    )
}
