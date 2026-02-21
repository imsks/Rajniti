import { ELECTION_TYPES } from "./constants"

/**
 * Get the human-readable name for an election type.
 */
const getElectionName = (electionType: string): string => {
    return ELECTION_TYPES[electionType as keyof typeof ELECTION_TYPES] ?? electionType
}

/**
 * Get party initials from the full party name.
 * e.g. "Bharatiya Janata Party" → "BJP"
 */
const getPartyInitials = (partyName: string): string => {
    return partyName
        .split(" ")
        .filter((w) => w.length > 2)
        .slice(0, 4)
        .map((w) => w[0])
        .join("")
        .toUpperCase()
}

export { getElectionName, getPartyInitials }
