"use client"

import type { Citation } from "@/types/politician"
import { ExternalLink } from "lucide-react"
import { useAnalytics } from "@/hooks/useAnalytics"

type CitationLinkProps = {
    citation?: Citation | null
    /** Short description for accessibility, e.g. "Education", "2024 election" */
    label: string
    className?: string
}

export function CitationLink({ citation, label, className = "" }: CitationLinkProps) {
    const { trackEvent } = useAnalytics()

    if (!citation?.link) return null
    let host = ""
    try {
        host = new URL(citation.link).hostname
    } catch {
        host = "source"
    }
    return (
        <a
            href={citation.link}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`${label} — source ${citation.source}`}
            title={`${citation.source} · ${host}`}
            className={`inline-flex items-center align-middle text-gray-400 hover:text-orange-500 dark:hover:text-orange-400 transition-colors ${className}`}
            onClick={() =>
                trackEvent("citation_link_click", {
                    citation_label: label,
                    source: citation.source ?? host,
                    url: citation.link!,
                })
            }
        >
            <ExternalLink className="w-3.5 h-3.5" aria-hidden />
        </a>
    )
}
