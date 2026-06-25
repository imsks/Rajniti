"use client"

import { useEffect, useId, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { Search, SlidersHorizontal, Check, ChevronDown, X, Plus } from "lucide-react"
import StateSelect from "@/components/politicians/StateSelect"
import {
    buildPoliticiansPath,
    type PoliticiansListFilters,
} from "@/components/politicians/PoliticiansDirectory"
import { getPartyColor, getPartyAcronym } from "@/lib/constants/partyColors"

interface PoliticiansFiltersProps {
    filters: PoliticiansListFilters
    states: string[]
    parties: string[]
}

// Active-state color classes (light + dark) for the MP / MLA type toggle.
const TYPE_ACTIVE_CLASS: Record<"MP" | "MLA", string> = {
    MP: "bg-blue-100 text-blue-700 border-blue-500 font-semibold dark:bg-blue-900/40 dark:text-blue-300 dark:border-blue-400",
    MLA: "bg-purple-100 text-purple-700 border-purple-500 font-semibold dark:bg-purple-900/40 dark:text-purple-300 dark:border-purple-400",
}

const PANEL_OPEN_KEY = "rajniti:filtersPanelOpen"

export default function PoliticiansFilters({
    filters,
    states,
    parties,
}: PoliticiansFiltersProps) {
    const router = useRouter()
    const [panelOpen, setPanelOpen] = useState(false)
    const [query, setQuery] = useState(filters.q ?? "")
    const [partyOpen, setPartyOpen] = useState(false)
    const [partySearch, setPartySearch] = useState("")
    const popoverRef = useRef<HTMLDivElement>(null)
    const searchInputRef = useRef<HTMLInputElement>(null)
    const listboxId = useId()

    // Persist the panel's open/closed state across filter navigations (each
    // selection re-renders the page from the server and remounts this component),
    // so only the Filters button toggles it — selecting a filter never collapses it.
    useEffect(() => {
        try {
            // Read after mount (not during render) to avoid an SSR hydration mismatch.
            setPanelOpen(sessionStorage.getItem(PANEL_OPEN_KEY) === "1")
        } catch {
            /* sessionStorage unavailable — keep default closed */
        }
    }, [])

    function togglePanel() {
        setPanelOpen((v) => {
            const next = !v
            try {
                sessionStorage.setItem(PANEL_OPEN_KEY, next ? "1" : "0")
            } catch {
                /* ignore */
            }
            return next
        })
    }

    const selected = filters.parties ?? []

    // Name search is not a "filter" — it does not count toward the Filters badge.
    const activeCount =
        (filters.type ? 1 : 0) + (filters.stateSlug ? 1 : 0) + selected.length

    // Close the party popover on outside click.
    useEffect(() => {
        if (!partyOpen) return
        function onClick(e: MouseEvent) {
            if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
                setPartyOpen(false)
            }
        }
        document.addEventListener("mousedown", onClick)
        return () => document.removeEventListener("mousedown", onClick)
    }, [partyOpen])

    function go(next: PoliticiansListFilters) {
        router.push(buildPoliticiansPath(1, next))
    }

    // Native search "×" (clear) fires a `search` event — when it empties the field
    // while a search is active, reset the list back to the full unsearched results.
    useEffect(() => {
        const el = searchInputRef.current
        if (!el) return
        function onNativeSearch() {
            if (el!.value === "" && filters.q) {
                go({ ...filters, q: undefined })
            }
        }
        el.addEventListener("search", onNativeSearch)
        return () => el.removeEventListener("search", onNativeSearch)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filters])

    function submitSearch(e: React.FormEvent) {
        e.preventDefault()
        go({ ...filters, q: query.trim() || undefined })
    }

    function setType(type?: "MP" | "MLA") {
        // Preserve state, search and party — type composes with all of them.
        go({ ...filters, type })
    }

    function toggleParty(party: string) {
        const next = selected.includes(party)
            ? selected.filter((p) => p !== party)
            : [...selected, party]
        go({ ...filters, parties: next.length > 0 ? next : undefined })
    }

    function clearAll() {
        setQuery("")
        router.push("/politicians")
    }

    const isAll = !filters.type
    const filteredParties = partySearch.trim()
        ? parties.filter((p) =>
              p.toLowerCase().includes(partySearch.trim().toLowerCase()),
          )
        : parties

    return (
        <div className="mb-8">
            {/* Search row */}
            <div className="flex items-center gap-3">
                <form onSubmit={submitSearch} className="flex items-center gap-3 flex-1">
                    <div className="relative flex-1">
                        <Search
                            size={16}
                            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                        />
                        <input
                            ref={searchInputRef}
                            type="search"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Search by Name…"
                            aria-label="Search politicians by name"
                            className="w-full h-12 pl-9 pr-4 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-orange-300 dark:focus:ring-orange-600"
                        />
                    </div>
                    <button
                        type="submit"
                        className="shrink-0 h-12 px-6 rounded-lg bg-orange-600/90 hover:bg-orange-600 text-white text-sm font-semibold transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-orange-300 dark:focus:ring-orange-600"
                    >
                        Search
                    </button>
                </form>

                <button
                    type="button"
                    onClick={togglePanel}
                    aria-expanded={panelOpen}
                    className={`flex items-center gap-2 h-12 px-4 rounded-lg border text-sm font-medium transition-colors cursor-pointer ${
                        panelOpen || activeCount > 0
                            ? "bg-orange-100 text-orange-700 border-orange-400 dark:border-orange-500 dark:text-orange-400 dark:bg-orange-900/20 font-semibold"
                            : "border-orange-400 hover:border-orange-500 hover:bg-orange-100 dark:border-orange-400 text-gray-700 dark:text-gray-300 dark:bg-orange-900/20 dark:hover:bg-orange-800/20"
                    }`}
                >
                    <SlidersHorizontal size={15} />
                    Filters
                    {activeCount > 0 && (
                        <span className="inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full bg-orange-600 text-white text-[11px] font-bold leading-none">
                            {activeCount}
                        </span>
                    )}
                </button>
            </div>

            {/* Collapsible panel */}
            {panelOpen && (
                <div className="mt-3 rounded-xl bg-gray-50/50 dark:bg-gray-800/40 border border-orange-200 dark:border-gray-700/60 px-4 py-3.5">
                    <div className="flex flex-wrap items-start gap-x-6 gap-y-4">
                        {/* A) State */}
                        <div className="flex flex-col gap-1.5">
                            <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                                State
                            </span>
                            <StateSelect states={states} filters={filters} />
                        </div>

                        {/* B) Type toggle */}
                        <div className="flex flex-col gap-1.5">
                            <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                                Type
                            </span>
                            <div className="flex">
                                <button
                                    type="button"
                                    onClick={() => setType(undefined)}
                                    className={`h-[38px] px-4 text-sm font-medium rounded-l-lg border cursor-pointer transition-colors ${
                                        isAll
                                            ? "bg-orange-100 text-orange-600 border-orange-500 dark:bg-orange-900/30 font-semibold dark:border-orange-500"
                                            : "bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800"
                                    }`}
                                >
                                    All
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setType("MP")}
                                    className={`h-[38px] px-4 text-sm font-medium border cursor-pointer transition-colors ${
                                        filters.type === "MP"
                                            ? TYPE_ACTIVE_CLASS.MP
                                            : "bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800"
                                    }`}
                                >
                                    MPs
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setType("MLA")}
                                    className={`h-[38px] px-4 text-sm font-medium rounded-r-lg border cursor-pointer transition-colors ${
                                        filters.type === "MLA"
                                            ? TYPE_ACTIVE_CLASS.MLA
                                            : "bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800"
                                    }`}
                                >
                                    MLAs
                                </button>
                            </div>
                        </div>

                        {/* C) Party multi-select */}
                        <div className="flex flex-col gap-1.5 min-w-[220px]">
                            <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                                Party
                            </span>
                            <div className="flex flex-wrap items-center gap-1.5 mt-1">
                                {selected.map((party) => {
                                    const c = getPartyColor(party)
                                    return (
                                        <button
                                            key={party}
                                            type="button"
                                            onClick={() => toggleParty(party)}
                                            style={{ backgroundColor: c.bg, color: c.darkText }}
                                            className="inline-flex items-center gap-1 h-[30px] pl-2 pr-1.5 rounded-full text-xs font-medium cursor-pointer"
                                            aria-label={`Remove ${party} filter`}
                                        >
                                            <Check size={12} />
                                            <span className="max-w-[140px] truncate">
                                                {getPartyAcronym(party)}
                                            </span>
                                            <X size={12} className="opacity-70" />
                                        </button>
                                    )
                                })}

                                {/* Popover opener */}
                                <div className="relative" ref={popoverRef}>
                                    <button
                                        type="button"
                                        onClick={() => setPartyOpen((v) => !v)}
                                        aria-expanded={partyOpen}
                                        aria-controls={listboxId}
                                        className="inline-flex items-center gap-1 h-[30px] px-2.5 rounded-full border bg-white hover:bg-orange-100  hover:border-orange-500 border-dashed border-gray-300 dark:border-gray-600 text-xs font-medium text-gray-600 dark:text-gray-300 dark:hover:bg-gray-800 cursor-pointer"
                                    >
                                        <Plus size={13} />
                                        {selected.length > 0 ? "Add" : "Party"}
                                        <ChevronDown size={13} className="opacity-60" />
                                    </button>

                                    {partyOpen && (
                                        <div
                                            id={listboxId}
                                            className="absolute left-0 top-full mt-1.5 z-30 w-64 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-lg"
                                        >
                                            <div className="p-2 border-b border-gray-100 dark:border-gray-800">
                                                <input
                                                    autoFocus
                                                    value={partySearch}
                                                    onChange={(e) => setPartySearch(e.target.value)}
                                                    placeholder="Search parties…"
                                                    className="w-full h-8 px-2.5 rounded-md border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-1 focus:ring-orange-300"
                                                />
                                            </div>
                                            <div className="max-h-60 overflow-y-auto py-1">
                                                {filteredParties.length === 0 ? (
                                                    <p className="px-3 py-2 text-xs text-gray-400">
                                                        No parties found.
                                                    </p>
                                                ) : (
                                                    filteredParties.map((party) => {
                                                        const c = getPartyColor(party)
                                                        const isSel = selected.includes(party)
                                                        return (
                                                            <button
                                                                key={party}
                                                                type="button"
                                                                onClick={() => toggleParty(party)}
                                                                className="flex items-center gap-2 w-full px-3 py-1.5 text-left text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
                                                            >
                                                                <span
                                                                    className="shrink-0 inline-flex items-center justify-center w-4 h-4 rounded-sm border"
                                                                    style={{
                                                                        borderColor: c.text,
                                                                        backgroundColor: isSel
                                                                            ? c.text
                                                                            : "transparent",
                                                                    }}
                                                                >
                                                                    {isSel && (
                                                                        <Check
                                                                            size={11}
                                                                            className="text-white"
                                                                        />
                                                                    )}
                                                                </span>
                                                                <span
                                                                    className="shrink-0 w-2 h-2 rounded-full"
                                                                    style={{ backgroundColor: c.text }}
                                                                />
                                                                <span className="truncate">
                                                                    {party}
                                                                </span>
                                                            </button>
                                                        )
                                                    })
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Clear all — far right */}
                        {activeCount > 0 && (
                            <button
                                type="button"
                                onClick={clearAll}
                                className="ml-auto self-center text-xs font-medium text-gray-500 dark:text-gray-400 hover:text-orange-600 dark:hover:text-orange-400 cursor-pointer"
                            >
                                Clear all
                            </button>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
