import type { ElectionType } from "@/types/politician"

// Color classes carry light + dark variants. Geometry stays inline below.
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
        <span
            className={`inline-flex items-center shrink-0 ${colorClass} ${className}`}
            style={{
                borderRadius: "20px",
                fontSize: "10px",
                fontWeight: 600,
                letterSpacing: "0.2px",
                padding: "3px 10px",
                lineHeight: 1,
                height: "20px",
            }}
        >
            {type}
        </span>
    )
}
