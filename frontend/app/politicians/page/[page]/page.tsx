import type { Metadata } from "next"
import renderPoliticiansDirectory, {
    generateDirectoryMetadata,
} from "@/lib/politicians/directory-page"
import { parsePartyParam } from "@/lib/politicians/directory"

export const dynamic = "force-dynamic"

export async function generateMetadata({
    params,
    searchParams,
}: {
    params: Promise<{ page: string }>
    searchParams: Promise<{ q?: string; party?: string }>
}): Promise<Metadata> {
    const { page: pageStr } = await params
    const { q, party } = await searchParams
    const page = Math.max(1, parseInt(pageStr, 10) || 1)
    return generateDirectoryMetadata(page, { q, parties: parsePartyParam(party) })
}

export default async function PoliticiansPaginatedPage({
    params,
    searchParams,
}: {
    params: Promise<{ page: string }>
    searchParams: Promise<{ q?: string; party?: string }>
}) {
    const { page: pageStr } = await params
    const { q, party } = await searchParams
    const page = Math.max(1, parseInt(pageStr, 10) || 1)
    return renderPoliticiansDirectory({
        page,
        filters: { q, parties: parsePartyParam(party) },
    })
}
