import type { Metadata } from "next"
import { notFound } from "next/navigation"
import renderPoliticiansDirectory, {
    generateDirectoryMetadata,
} from "@/lib/politicians/directory-page"
import { parsePartyParam } from "@/lib/politicians/directory"
import { fetchStates } from "@/lib/api/politicians-catalog-server"
import { resolveStateFromSlug, slugifySegment } from "@/lib/seo/slugify"

export const dynamic = "force-dynamic"

async function resolveStateFilters(stateSlug: string) {
    const states = await fetchStates()
    const state = resolveStateFromSlug(stateSlug, states)
    if (!state) return null
    return { state, stateSlug: slugifySegment(state) }
}

function parseType(type?: string): "MP" | "MLA" | undefined {
    return type === "MP" || type === "MLA" ? type : undefined
}

export async function generateMetadata({
    params,
    searchParams,
}: {
    params: Promise<{ stateSlug: string; page: string }>
    searchParams: Promise<{ q?: string; party?: string; type?: string }>
}): Promise<Metadata> {
    const { stateSlug, page: pageStr } = await params
    const { q, party, type } = await searchParams
    const resolved = await resolveStateFilters(stateSlug)
    if (!resolved) return { title: "State not found", robots: { index: false } }

    const page = Math.max(1, parseInt(pageStr, 10) || 1)
    return generateDirectoryMetadata(page, {
        ...resolved,
        type: parseType(type),
        q,
        parties: parsePartyParam(party),
    })
}

export default async function PoliticiansStatePaginatedPage({
    params,
    searchParams,
}: {
    params: Promise<{ stateSlug: string; page: string }>
    searchParams: Promise<{ q?: string; party?: string; type?: string }>
}) {
    const { stateSlug, page: pageStr } = await params
    const { q, party, type } = await searchParams
    const resolved = await resolveStateFilters(stateSlug)
    if (!resolved) notFound()

    const page = Math.max(1, parseInt(pageStr, 10) || 1)
    return renderPoliticiansDirectory({
        page,
        filters: {
            ...resolved,
            type: parseType(type),
            q,
            parties: parsePartyParam(party),
        },
    })
}
