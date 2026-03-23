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
}

export interface Education {
    qualification: string
    institution?: string | null
    year_completed?: number | null
}

export interface ElectionRecord {
    year: number
    type: string
    state: string
    constituency: string
    party: string
    status: string
}

export interface PoliticalBackground {
    elections: ElectionRecord[]
    summary?: string | null
}

export interface CrimeRecord {
    name: string
    type?: CrimeType | null
    year?: number | null
}

export interface Politician {
    id: string
    name: string
    /**
     * SEO-friendly slug generated in the backend.
     * When missing (older data), UI will fall back to UUID URLs.
     */
    slug?: string | null
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

    notes?: string | null
}

/** Client-side computed stats */
export interface PoliticianStats {
    total: number
    totalStates: number
    totalParties: number
    topParty: string
}
