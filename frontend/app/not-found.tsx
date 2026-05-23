import type { Metadata } from "next"
import Link from "next/link"
import { SITE_NAME } from "@/lib/seo/site"

export const metadata: Metadata = {
    title: "Page not found",
    robots: { index: false, follow: false },
}

export default function NotFound() {
    return (
        <main className="min-h-screen flex flex-col items-center justify-center px-4 bg-linear-to-b from-orange-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">404</h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6 text-center">
                This page could not be found on {SITE_NAME}.
            </p>
            <div className="flex gap-4">
                <Link
                    href="/"
                    className="px-4 py-2 rounded-lg bg-orange-600 text-white hover:bg-orange-700 transition"
                >
                    Home
                </Link>
                <Link
                    href="/politicians"
                    className="px-4 py-2 rounded-lg border border-orange-300 text-orange-700 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-gray-800 transition"
                >
                    Browse Politicians
                </Link>
            </div>
        </main>
    )
}
