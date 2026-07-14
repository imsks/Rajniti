import { Badge } from "@sutra/ui"
import type { ElectionType } from "@/types/politician"

// Domain colour mapping stays in Rajniti; the pill itself is a Sutra Badge.
const ROLE_CLASSES: Record<ElectionType, string> = {
    MP: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
    MLA: "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
}

interface RoleBadgeProps {
    type: ElectionType
    className?: string
}

export default function RoleBadge({ type, className = "" }: RoleBadgeProps) {
    const colorClass = ROLE_CLASSES[type] ?? ROLE_CLASSES.MP
    return (
        <Badge
            size="sm"
            className={`shrink-0 ${colorClass} ${className}`}
            style={{
                fontSize: "10px",
                fontWeight: 600,
                letterSpacing: "0.2px",
                padding: "3px 10px",
                lineHeight: 1,
                height: "20px",
            }}
        >
            {type}
        </Badge>
    )
}
