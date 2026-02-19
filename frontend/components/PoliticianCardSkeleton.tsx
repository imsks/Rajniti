"use client"

import { motion } from "framer-motion"

export default function PoliticianCardSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 overflow-hidden relative">
      {/* shimmer overlay */}
      <motion.div
        className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-gray-100 to-transparent"
        animate={{ x: ["-100%", "100%"] }}
        transition={{ duration: 1.2, repeat: Infinity, ease: "linear" }}
      />

      <div className="flex items-start gap-4 relative">
        {/* photo */}
        <div className="h-16 w-16 rounded-xl bg-gray-200 shrink-0" />

        <div className="flex-1 space-y-3">
          {/* name */}
          <div className="h-4 w-3/4 rounded bg-gray-200" />

          {/* constituency */}
          <div className="h-3 w-2/3 rounded bg-gray-200" />

          {/* party */}
          <div className="h-3 w-1/2 rounded bg-gray-200" />
        </div>
      </div>

      {/* bottom badges */}
      <div className="mt-5 flex gap-2 relative">
        <div className="h-7 w-20 rounded-full bg-gray-200" />
        <div className="h-7 w-24 rounded-full bg-gray-200" />
      </div>
    </div>
  )
}
