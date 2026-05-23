import type { Metadata } from "next"
import renderPoliticiansDirectory, {
    generateDirectoryMetadata,
} from "@/lib/politicians/directory-page"

export const dynamic = "force-dynamic"

export async function generateMetadata({
    params,
    searchParams,
}: {
    params: Promise<{ page: string }>
    searchParams: Promise<{ q?: string }>
}): Promise<Metadata> {
    const { page: pageStr } = await params
    const { q } = await searchParams
    const page = Math.max(1, parseInt(pageStr, 10) || 1)
    return generateDirectoryMetadata(page, { type: "MLA", q })
}

export default async function PoliticiansMlaPaginatedPage({
    params,
    searchParams,
}: {
    params: Promise<{ page: string }>
    searchParams: Promise<{ q?: string }>
}) {
    const { page: pageStr } = await params
    const { q } = await searchParams
    const page = Math.max(1, parseInt(pageStr, 10) || 1)
    return renderPoliticiansDirectory({ page, filters: { type: "MLA", q } })
}
