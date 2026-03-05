/**
 * Help users find their MLA/MP via location or pincode → Google search.
 * Pure URL builder; geolocation + reverse geocode are async.
 */

/** Pure: build Google search URL for finding MLA/MP by pincode or area. */
export function buildGoogleSearchUrlForMlaMp(pincodeOrArea: string): string {
    const q = encodeURIComponent(
        `MLA MP for pincode ${pincodeOrArea.trim()} India`
    )
    return `https://www.google.com/search?q=${q}`
}

/** Reverse-geocode lat/lng to pincode using Nominatim (no API key). */
export async function getPincodeFromCoords(
    lat: number,
    lon: number
): Promise<string | null> {
    try {
        const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&addressdetails=1`
        const res = await fetch(url, {
            headers: { Accept: "application/json" },
        })
        const data = (await res.json()) as {
            address?: { postcode?: string; state_district?: string }
        }
        const postcode = data?.address?.postcode
        if (postcode && String(postcode).trim()) return String(postcode).trim()
        const area = data?.address?.state_district
        if (area && String(area).trim()) return String(area).trim()
    } catch {
        // ignore
    }
    return null
}

/** Get current position; returns [lat, lon] or null. */
export function getCurrentPosition(): Promise<{ lat: number; lon: number } | null> {
    return new Promise((resolve) => {
        if (!navigator?.geolocation) {
            resolve(null)
            return
        }
        navigator.geolocation.getCurrentPosition(
            (pos) =>
                resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
            () => resolve(null),
            { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
        )
    })
}
