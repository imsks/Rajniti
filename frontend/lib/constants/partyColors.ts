/**
 * Party → color mapping for chips, dots, card accents and party text.
 *
 * Keys are canonical abbreviations. Because the underlying data stores full
 * party names (e.g. "Bharatiya Janata Party"), `getPartyColor` normalizes an
 * incoming party string through PARTY_ALIASES before lookup. Anything not
 * recognized falls back to a neutral gray.
 */

export interface PartyColor {
    /** Border + light-mode text hex. */
    text: string
    /** Darker text hex (used where stronger contrast is needed). */
    darkText: string
    /** Light background hex (chips, accents). */
    bg: string
}

export const FALLBACK_PARTY_COLOR: PartyColor = {
    text: "#888780",
    darkText: "#2C2C2A",
    bg: "#F1EFE8",
}

/** Canonical abbreviation → color. */
export const PARTY_COLORS: Record<string, PartyColor> = {
    BJP: { text: "#BA7517", darkText: "#633806", bg: "#FAEEDA" },
    INC: { text: "#185FA5", darkText: "#042C53", bg: "#E6F1FB" },
    AAP: { text: "#0F6E56", darkText: "#04342C", bg: "#E1F5EE" },
    BSP: { text: "#534AB7", darkText: "#26215C", bg: "#EEEDFE" },
    "CPI(M)": { text: "#A32D2D", darkText: "#501313", bg: "#FCEBEB" },
    TDP: { text: "#993C1D", darkText: "#4A1B0C", bg: "#FAECE7" },
    BRS: { text: "#D4537E", darkText: "#4B1528", bg: "#FBEAF0" },
    TMC: { text: "#639922", darkText: "#173404", bg: "#EAF3DE" },
    DMK: { text: "#A32D2D", darkText: "#501313", bg: "#FCEBEB" },
    "Shiv Sena": { text: "#BA7517", darkText: "#633806", bg: "#FAEEDA" },
    NCP: { text: "#185FA5", darkText: "#042C53", bg: "#E6F1FB" },
    "JD(U)": { text: "#0F6E56", darkText: "#04342C", bg: "#E1F5EE" },
    SP: { text: "#534AB7", darkText: "#26215C", bg: "#EEEDFE" },
    RJD: { text: "#639922", darkText: "#173404", bg: "#EAF3DE" },
    AIMM: { text: "#20783B", darkText: "#17542a", bg: "#e4ffec" },
    AIUDF: { text: "#008b00", darkText: "#007100", bg: "#e2ffe2" },
    Independent: { text: "#888780", darkText: "#2C2C2A", bg: "#F1EFE8" },
}

/**
 * Full party names (and common variants) → canonical abbreviation key.
 * Normalized to lowercase, collapsed whitespace for matching.
 */
const PARTY_ALIASES: Record<string, string> = {
    // BJP
    "bharatiya janata party": "BJP",
    "bharatiya janata party (bjp)": "BJP",
    bjp: "BJP",
    // INC
    "indian national congress": "INC",
    inc: "INC",
    congress: "INC",
    // AAP
    "aam aadmi party": "AAP",
    aap: "AAP",
    // BSP
    "bahujan samaj party": "BSP",
    bsp: "BSP",
    // CPI(M)
    cpm: "CPI(M)",
    "cpi(m)": "CPI(M)",
    "communist party of india (marxist)": "CPI(M)",
    // TDP
    "telugu desam": "TDP",
    "telugu desam party": "TDP",
    tdp: "TDP",
    // BRS
    "bharat rashtra samithi": "BRS",
    brs: "BRS",
    // TMC
    "all india trinamool congress": "TMC",
    "trinamool congress": "TMC",
    tmc: "TMC",
    // DMK
    "dravida munnetra kazhagam": "DMK",
    dmk: "DMK",
    // Shiv Sena
    "shiv sena": "Shiv Sena",
    "shiv sena (uddhav balasaheb thackrey)": "Shiv Sena",
    // NCP
    "nationalist congress party": "NCP",
    "nationalist congress party – sharadchandra pawar": "NCP",
    ncp: "NCP",
    // JD(U)
    "janata dal (united)": "JD(U)",
    "jd(u)": "JD(U)",
    // SP
    "samajwadi party": "SP",
    sp: "SP",
    // RJD
    "rashtriya janata dal": "RJD",
    rjd: "RJD",
    // AIMM
    "all india majlis-e-ittehadul muslimeen": "AIMM",
    "all india majlis-e-ittehadul muslimeen (aimm)": "AIMM",
    // AIUDF
    "all india united democratic front": "AIUDF",
    "all india united democratic front (aiudf)": "AIUDF",
    aiudf: "AIUDF",
    // Independent
    independent: "Independent",
}

function normalize(value: string): string {
    return value.trim().toLowerCase().replace(/\s+/g, " ")
}

/** Resolve a party string (full name or abbreviation) to its color. */
export function getPartyColor(party?: string | null): PartyColor {
    if (!party) return FALLBACK_PARTY_COLOR
    const norm = normalize(party)

    // Direct key match (case-insensitive) against canonical keys.
    const directKey = Object.keys(PARTY_COLORS).find(
        (k) => normalize(k) === norm,
    )
    if (directKey) return PARTY_COLORS[directKey]

    // Alias lookup (full names / variants).
    const aliasKey = PARTY_ALIASES[norm]
    if (aliasKey && PARTY_COLORS[aliasKey]) return PARTY_COLORS[aliasKey]

    return FALLBACK_PARTY_COLOR
}

// Words skipped when generating an acronym for an unmapped party.
const ACRONYM_STOPWORDS = new Set(["of", "and", "the", "&"])

/**
 * Short display label for a party — e.g. "Bharatiya Janata Party" → "BJP".
 * Known parties map to their canonical abbreviation; unknown ones get an
 * acronym built from the initials of their significant words.
 */
export function getPartyAcronym(party?: string | null): string {
    if (!party) return ""
    const norm = normalize(party)

    const directKey = Object.keys(PARTY_COLORS).find(
        (k) => normalize(k) === norm,
    )
    if (directKey) return directKey

    const aliasKey = PARTY_ALIASES[norm]
    if (aliasKey) return aliasKey

    const acronym = party
        .trim()
        .split(/\s+/)
        .filter((w) => w && !ACRONYM_STOPWORDS.has(w.toLowerCase()))
        .map((w) => w[0]?.toUpperCase() ?? "")
        .join("")
        .slice(0, 5)
    return acronym || party
}

/** Canonical party key → logo filename under /public/party. */
const PARTY_LOGOS: Record<string, string> = {
    BJP: "bjp.svg",
    INC: "inc.svg",
    AAP: "aap.svg",
    BSP: "bsp.svg",
    "CPI(M)": "cpi.svg",
    TDP: "tdp.svg",
    BRS: "brs.svg",
    TMC: "tmc.svg",
    DMK: "dmk.svg",
    "Shiv Sena": "shivSena.svg",
    NCP: "ncp.svg",
    "JD(U)": "jdu.svg",
    SP: "sp.svg",
    RJD: "rjd.svg",
    AIMM: "aimm.svg",
    AIUDF: "aiudf.svg",
}

/**
 * Public path to a party's saved logo, matched by name. Returns null when the
 * party has no saved logo (caller should then render without a logo tile).
 */
export function getPartyLogo(party?: string | null): string | null {
    if (!party) return null
    const norm = normalize(party)

    const directKey = Object.keys(PARTY_COLORS).find(
        (k) => normalize(k) === norm,
    )
    const key = directKey ?? PARTY_ALIASES[norm]
    if (key && PARTY_LOGOS[key]) return `/party/${PARTY_LOGOS[key]}`

    return null
}
