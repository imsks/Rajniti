import type { Metadata } from "next"
import renderPoliticiansDirectory, {
    generateDirectoryMetadata,
} from "@/lib/politicians/directory-page"
import { parsePartyParam } from "@/lib/politicians/directory"

export const dynamic = "force-dynamic"

export async function generateMetadata({
    searchParams,
}: {
    searchParams: Promise<{ q?: string; party?: string }>
}): Promise<Metadata> {
    const { q, party } = await searchParams
    return generateDirectoryMetadata(1, { q, parties: parsePartyParam(party) })
}

export default async function PoliticiansPage({
    searchParams,
}: {
    searchParams: Promise<{ q?: string; party?: string }>
}) {
    const { q, party } = await searchParams
    return renderPoliticiansDirectory({
        page: 1,
        filters: { q, parties: parsePartyParam(party) },
    })
}
