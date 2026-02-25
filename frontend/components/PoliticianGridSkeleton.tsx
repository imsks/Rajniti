"use client"

import PoliticianCardSkeleton from "./PoliticianCardSkeleton"

export default function PoliticianGridSkeleton({ count = 9 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {Array.from({ length: count }).map((_, i) => (
        <PoliticianCardSkeleton key={i} />
      ))}
    </div>
  )
}
