"use client"

import { useRouter } from "next/navigation"
import { ChevronDown } from "lucide-react"
import { slugifySegment } from "@/lib/seo/slugify"
import {
    buildPoliticiansPath,
    type PoliticiansListFilters,
} from "@/components/politicians/PoliticiansDirectory"

interface StateSelectProps {
    states: string[]
    /** Current active filters — type, search and parties are preserved on change. */
    filters: PoliticiansListFilters
}

export default function StateSelect({ states, filters }: StateSelectProps) {
    const router = useRouter()

    if (states.length === 0) return null

    return (
        <div className="relative inline-block">
            <select
                value={filters.stateSlug ?? ""}
                onChange={(e) => {
                    const slug = e.target.value
                    // State composes with type/search/party — preserve them all.
                    const next: PoliticiansListFilters = {
                        ...filters,
                        stateSlug: slug || undefined,
                        state: slug ? filters.state : undefined,
                    }
                    router.push(buildPoliticiansPath(1, next))
                }}
                className="appearance-none pl-3 pr-9 py-2 h-[38px] rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-orange-300 dark:focus:ring-orange-600"
                aria-label="Filter by state"
            >
                <option value="">All states</option>
                {states.map((state) => (
                    <option key={state} value={slugifySegment(state)}>
                        {state}
                    </option>
                ))}
            </select>
            <ChevronDown
                size={16}
                className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
            />
        </div>
    )
}
