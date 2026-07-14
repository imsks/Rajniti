"use client"

import { useRouter } from "next/navigation"
import { Select } from "@sutra_ui/ui"
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
        <div className="inline-block w-44">
            <Select
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
                aria-label="Filter by state"
            >
                <option value="">All states</option>
                {states.map((state) => (
                    <option key={state} value={slugifySegment(state)}>
                        {state}
                    </option>
                ))}
            </Select>
        </div>
    )
}
