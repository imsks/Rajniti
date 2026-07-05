import type { Metadata } from "next"
import renderPoliticiansDirectory, {
    generateDirectoryMetadata,
    resolveStateBySlug,
} from "@/lib/politicians/directory-page"
import { parsePartyParam } from "@/components/politicians/PoliticiansDirectory"

export const dynamic = "force-dynamic"

export async function generateMetadata({
    params,
    searchParams,
}: {
    params: Promise<{ page?: string }>
    searchParams: Promise<{ q?: string; party?: string; state?: string }>
}): Promise<Metadata> {
    const { page: pageStr } = await params
    const { q, party, state } = await searchParams
    const page = pageStr ? Math.max(1, parseInt(pageStr, 10) || 1) : 1
    const resolvedState = await resolveStateBySlug(state)
    return generateDirectoryMetadata(page, {
        type: "MLA",
        q,
        parties: parsePartyParam(party),
        ...(resolvedState ?? {}),
    })
}

export default async function PoliticiansMlaPage({
    params,
    searchParams,
}: {
    params: Promise<{ page?: string }>
    searchParams: Promise<{ q?: string; party?: string; state?: string }>
}) {
    const { page: pageStr } = await params
    const { q, party, state } = await searchParams
    const page = pageStr ? Math.max(1, parseInt(pageStr, 10) || 1) : 1
    const resolvedState = await resolveStateBySlug(state)
    return renderPoliticiansDirectory({
        page,
        filters: {
            type: "MLA",
            q,
            parties: parsePartyParam(party),
            ...(resolvedState ?? {}),
        },
    })
}
