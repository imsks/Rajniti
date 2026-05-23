import type { Metadata } from "next"
import renderPoliticiansDirectory, {
    generateDirectoryMetadata,
} from "@/lib/politicians/directory-page"

export const dynamic = "force-dynamic"

export async function generateMetadata({
    searchParams,
}: {
    searchParams: Promise<{ q?: string }>
}): Promise<Metadata> {
    const { q } = await searchParams
    return generateDirectoryMetadata(1, { q })
}

export default async function PoliticiansPage({
    searchParams,
}: {
    searchParams: Promise<{ q?: string }>
}) {
    const { q } = await searchParams
    return renderPoliticiansDirectory({ page: 1, filters: { q } })
}
