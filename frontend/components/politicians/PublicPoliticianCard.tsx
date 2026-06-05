import Link from "next/link"
import { getPoliticianProfileHref, getParty, toTitleCase } from "@/lib/politicianUtils"
import type { Politician } from "@/types/politician"
import Image from "@/components/ui/Image"

interface PublicPoliticianCardProps {
    politician: Politician
}

export default function PublicPoliticianCard({ politician }: PublicPoliticianCardProps) {
    const party = getParty(politician)
    const isMp = politician.type === "MP"
    const href = getPoliticianProfileHref(politician)

    return (
        <article className="group rounded-xl border border-orange-100 dark:border-gray-700 bg-white dark:bg-gray-900 p-4 hover:shadow-md hover:border-orange-300 dark:hover:border-orange-700 transition">
            <Link href={href} className="block no-underline">
                <div className="flex items-start gap-3">
                    <div
                        className={`shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold text-white ${
                            isMp ? "bg-orange-600" : "bg-green-600"
                        }`}
                    >
                        {politician.photo ? (
                            <Image
                                src={politician.photo}
                                alt={politician.name}
                                className="w-full h-full object-cover rounded-full"
                            />
                        ) : (
                            politician.name.charAt(0)
                        )}
                    </div>
                    <div className="min-w-0 flex-1">
                        <h2 className="text-base font-semibold text-gray-900 dark:text-white group-hover:text-orange-600 dark:group-hover:text-orange-400 truncate">
                            {toTitleCase(politician.name)}
                        </h2>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                            {toTitleCase(politician.constituency)}, {politician.state}
                        </p>
                        <div className="flex flex-wrap gap-2 mt-2">
                            <span
                                className={`text-xs px-2 py-0.5 rounded-full ${
                                    isMp
                                        ? "bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300"
                                        : "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300"
                                }`}
                            >
                                {politician.type}
                            </span>
                            {party !== "—" && (
                                <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 truncate max-w-[140px]">
                                    {party}
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            </Link>
        </article>
    )
}
