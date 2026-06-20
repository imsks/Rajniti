/**
 * Politician types — mirrors the backend Pydantic schema.
 */

export type ElectionType = "MP" | "MLA"

export type CrimeType =
    | "MURDER"
    | "RAPE"
    | "KIDNAPPING"
    | "THEFT"
    | "CORRUPTION"
    | "ECONOMIC"
    | "OTHERS"

export type CitationSource =
    | "ECI"
    | "MYNETA"
    | "GOV_WEBSITE"
    | "NEWS"
    | "OTHERS"

export interface Citation {
    link: string
    source: CitationSource
}

export interface Contact {
    email?: string | null
    phone?: string | null
    address?: string | null
}

export interface SocialMedia {
    twitter?: string | null
    facebook?: string | null
    instagram?: string | null
    linkedin?: string | null
    youtube?: string | null
    website?: string | null
}

export interface FamilyMember {
    name: string
    relation: string
    photo?: string | null
    social_media?: SocialMedia | null
    citation?: Citation | null
}

export interface Education {
    qualification: string
    institution?: string | null
    year_completed?: number | null
    citation?: Citation | null
}

export interface ElectionRecord {
    year: number
    type: string
    state: string
    constituency: string
    party: string
    status: string
    citation?: Citation | null
}

export interface PoliticalBackground {
    elections: ElectionRecord[]
    summary?: string | null
    summary_citation?: Citation | null
}

export interface CrimeRecord {
    name: string
    type?: CrimeType | null
    year?: number | null
    citation?: Citation | null
}

export interface AffidavitAsset {
    description: string
    value_inr?: number | null
    citation?: Citation | null
}

export interface FinancialDisclosure {
    total_assets_inr?: number | null
    total_liabilities_inr?: number | null
    net_worth_inr?: number | null
    movable_assets?: AffidavitAsset[] | null
    immovable_assets?: AffidavitAsset[] | null
    liabilities?: AffidavitAsset[] | null
    citation?: Citation | null
    as_of_election?: string | null
}

export interface Politician {
    id: string
    name: string
    /**
     * SEO-friendly slug generated in the backend.
     * When missing (older data), UI will fall back to UUID URLs.
     */
    slug?: string | null
    /**
     * ISO format timestamp when politician data was last updated.
     */
    updated_at?: string | null
    photo?: string | null
    state: string
    constituency: string
    type: ElectionType

    education?: Education[] | null
    family_background?: FamilyMember[] | null
    criminal_records?: CrimeRecord[] | null

    social_media?: SocialMedia | null
    contact?: Contact | null

    political_background: PoliticalBackground

    performance?: {
        attendance: number
        questions: number
        debates: number
    }
    contact_citations?: Partial<Record<keyof Contact, Citation>> | null
    social_media_citations?: Partial<Record<keyof SocialMedia, Citation>> | null
    performance_citations?: Partial<
        Record<"attendance" | "questions" | "debates", Citation>
    > | null
    citation_audit?: Record<string, unknown> | null
    financial_disclosure?: FinancialDisclosure | null
    source_sync?: Record<string, string> | null
}

/** Client-side computed stats */
export interface PoliticianStats {
    total: number
    totalStates: number
    totalParties: number
    topParty: string
}
