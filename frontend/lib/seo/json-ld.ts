import { getPoliticianProfileHref } from "@/lib/politicianUtils"
import { getParty } from "@/lib/politicianUtils"
import { getSiteUrl, SITE_NAME } from "@/lib/seo/site"
import type { Politician } from "@/types/politician"

export interface BreadcrumbItem {
    name: string
    path: string
}

export function buildWebSiteJsonLd(): Record<string, unknown> {
    const base = getSiteUrl()
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        name: SITE_NAME,
        url: base,
        description:
            "Explore Indian MPs and MLAs — political history, education, performance, and more.",
        potentialAction: {
            "@type": "SearchAction",
            target: {
                "@type": "EntryPoint",
                urlTemplate: `${base}/politicians?q={search_term_string}`,
            },
            "query-input": "required name=search_term_string",
        },
    }
}

export function buildBreadcrumbJsonLd(items: BreadcrumbItem[]): Record<string, unknown> {
    const base = getSiteUrl()
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        itemListElement: items.map((item, index) => ({
            "@type": "ListItem",
            position: index + 1,
            name: item.name,
            item: `${base}${item.path}`,
        })),
    }
}

export interface ItemListEntry {
    name: string
    href: string
}

export function buildItemListJsonLd(
    items: ItemListEntry[],
    listName: string
): Record<string, unknown> {
    const base = getSiteUrl()
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        name: listName,
        numberOfItems: items.length,
        itemListElement: items.map((item, index) => ({
            "@type": "ListItem",
            position: index + 1,
            name: item.name,
            url: `${base}${item.href}`,
        })),
    }
}

export function buildPersonJsonLd(
    politician: Politician,
    canonicalPath: string
): Record<string, unknown> {
    const base = getSiteUrl()
    const url = `${base}${canonicalPath}`
    const party = getParty(politician)
    const record: Record<string, unknown> = {
        "@context": "https://schema.org",
        "@type": "Person",
        name: politician.name,
        url,
        jobTitle:
            politician.type === "MP"
                ? "Member of Parliament"
                : "Member of Legislative Assembly",
        homeLocation: {
            "@type": "Place",
            name: `${politician.constituency}, ${politician.state}, India`,
        },
    }
    if (politician.photo) record.image = politician.photo
    if (party && party !== "—") {
        record.memberOf = { "@type": "Organization", name: party }
    }
    return record
}

export function buildPoliticianBreadcrumbJsonLd(
    politician: Politician
): Record<string, unknown> {
    return buildBreadcrumbJsonLd([
        { name: "Home", path: "/" },
        { name: "Politicians", path: "/politicians" },
        {
            name: politician.name,
            path: getPoliticianProfileHref(politician),
        },
    ])
}
