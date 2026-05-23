/**
 * Local storage for "My Politicians" (MP + MLA slots).
 * Pure parsing; get/set are the only I/O.
 */

export interface MyPoliticianIds {
    mpId: string | null
    mlaId: string | null
}

export const MY_POLITICIANS_STORAGE_KEY = "rajniti_my_politicians"

const DEFAULT_IDS: MyPoliticianIds = { mpId: null, mlaId: null }

/** Pure: parse JSON string to MyPoliticianIds; returns default on invalid/legacy. */
export function parseMyPoliticianIds(raw: string | null): MyPoliticianIds {
    if (raw === null || raw === "") return DEFAULT_IDS
    try {
        const parsed = JSON.parse(raw) as Record<string, unknown> | null
        if (parsed && typeof parsed === "object") {
            const mpId =
                typeof parsed.mpId === "string" ? parsed.mpId : null
            const mlaId =
                typeof parsed.mlaId === "string" ? parsed.mlaId : null
            return { mpId: mpId || null, mlaId: mlaId || null }
        }
    } catch {
        // ignore
    }
    return DEFAULT_IDS
}

/** Read from localStorage (SSR-safe). */
export function getMyPoliticianIds(): MyPoliticianIds {
    if (typeof window === "undefined") return DEFAULT_IDS
    return parseMyPoliticianIds(window.localStorage.getItem(MY_POLITICIANS_STORAGE_KEY))
}

/** Write to localStorage. */
export function setMyPoliticianIds(ids: MyPoliticianIds): void {
    if (typeof window === "undefined") return
    window.localStorage.setItem(MY_POLITICIANS_STORAGE_KEY, JSON.stringify(ids))
}
