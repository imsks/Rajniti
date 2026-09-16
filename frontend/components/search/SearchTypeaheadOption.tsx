"use client"

import Image from "next/image"
import PoliticianAvatar from "@/components/ui/PoliticianAvatar"
import RoleBadge from "@/components/politicians/RoleBadge"
import {
    getPartyColor,
    getPartyLogo,
    getPartyAcronym,
} from "@/lib/constants/partyColors"
import { toTitleCase, getParty } from "@/lib/politicianUtils"
import type { Politician } from "@/types/politician"

interface SearchTypeaheadOptionProps {
    politician: Politician
    index: number
    isHighlighted: boolean
    logoErrors: Set<string>
    onSelect: (politician: Politician) => void
    onHighlight: (index: number) => void
    onLogoError: (partyKey: string) => void
}

/**
 * A single typeahead suggestion row. The option itself is the interactive
 * control (no nested button) so listbox semantics stay valid.
 */
export default function SearchTypeaheadOption({
    politician,
    index,
    isHighlighted,
    logoErrors,
    onSelect,
    onHighlight,
    onLogoError,
}: SearchTypeaheadOptionProps) {
    const party = getParty(politician)
    const partyDisplay = party !== "—" ? party : null
    const partyColor = getPartyColor(partyDisplay)
    const partyLogo = getPartyLogo(partyDisplay)
    const partyKey = partyDisplay || ""
    const showLogo = Boolean(partyLogo) && !logoErrors.has(partyKey)

    return (
        <li
            id={`search-typeahead-option-${index}`}
            role="option"
            aria-selected={isHighlighted}
            onClick={() => onSelect(politician)}
            onMouseEnter={() => onHighlight(index)}
            className={`w-full px-4 py-2.5 flex items-center gap-3 text-left transition-colors cursor-pointer ${
                isHighlighted
                    ? "bg-orange-50 dark:bg-gray-800"
                    : "hover:bg-gray-50 dark:hover:bg-gray-800"
            }`}
        >
            <div className="flex items-center gap-3 flex-1 min-w-0">
                <PoliticianAvatar
                    photo={politician.photo}
                    name={politician.name}
                    party={partyDisplay}
                    size={36}
                />
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 dark:text-white truncate">
                            {toTitleCase(politician.name)}
                        </span>
                        <RoleBadge type={politician.type} />
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {toTitleCase(politician.constituency)}, {politician.state}
                    </p>
                </div>
            </div>

            <div className="shrink-0 flex items-center justify-center w-6 h-6">
                {showLogo && partyLogo ? (
                    <span className="relative w-5 h-5">
                        <Image
                            src={partyLogo}
                            alt={getPartyAcronym(partyDisplay) || ""}
                            fill
                            className="object-contain"
                            sizes="20px"
                            onError={() => onLogoError(partyKey)}
                        />
                    </span>
                ) : (
                    <span
                        className="w-3 h-3 rounded-full"
                        style={{
                            backgroundColor: partyColor.text,
                        }}
                        aria-label={
                            partyDisplay
                                ? getPartyAcronym(partyDisplay)
                                : "Independent"
                        }
                    />
                )}
            </div>
        </li>
    )
}
