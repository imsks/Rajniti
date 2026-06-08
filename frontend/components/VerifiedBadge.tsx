import { ShieldCheck } from "lucide-react"

interface VerifiedBadgeProps {
    /** Citation score in [0, 1], or null/undefined if unknown. */
    score?: number | null
    className?: string
}

/**
 * Hero chip showing what percentage of a politician's facts are independently
 * sourced.  Colour bands:
 *   - Green  (≥ 75 %) — high trust
 *   - Yellow (≥ 60 % and < 75 %) — moderate trust
 *   - Red    (< 60 %) — low trust
 *   - "Unverified" copy for 0 % (or missing score) instead of "0 % verified"
 */
export default function VerifiedBadge({ score, className = "" }: VerifiedBadgeProps) {
    const pct = score != null ? Math.round(score * 100) : 0

    if (pct === 0) {
        return (
            <span
                className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 ${className}`}
                title="No citations found — help us source this profile"
            >
                <ShieldCheck size={12} aria-hidden />
                Unverified — help us source this
            </span>
        )
    }

    const colorClass =
        pct >= 75
            ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
            : pct >= 60
              ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300"
              : "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300"

    return (
        <span
            className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${colorClass} ${className}`}
            title={`${pct}% of facts in this profile have a cited source`}
        >
            <ShieldCheck size={12} aria-hidden />
            {pct}% verified
        </span>
    )
}
