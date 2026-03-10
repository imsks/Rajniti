"use client"

import PoliticianCard from "@/components/PoliticianCard"
import PoliticianCardSkeleton from "@/components/PoliticianCardSkeleton"
import type { Politician } from "@/types/politician"

interface Props {
    politician?: Politician
    loading?: boolean
}

export default function PoliticianCardWrapper({ politician, loading = false }: Props) {
    if (loading || !politician) {
        return <PoliticianCardSkeleton />
    }
    return <PoliticianCard politician={politician} />
}
