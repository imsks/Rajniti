"use client"

import { useEffect } from "react"
import { Navbar, Footer } from "@/components/layout"
import Button from "@/components/ui/Button"
import Text from "@/components/ui/Text"

export default function PoliticianProfileError({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        console.error("[politician profile]", error)
    }, [error])

    return (
        <div className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
            <Navbar sticky />
            <div className="mx-auto max-w-lg px-4 py-24 text-center">
                <Text variant="h2" weight="bold" className="text-gray-900 dark:text-white mb-3">
                    Could not load this profile
                </Text>
                <Text variant="body" className="text-gray-600 dark:text-gray-400 mb-8">
                    The politician API may be unavailable. Ensure the backend is running and
                    API_URL / NEXT_PUBLIC_API_URL point to it.
                </Text>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <Button onClick={() => reset()} variant="primary">
                        Try again
                    </Button>
                    <Button href="/dashboard" variant="secondary">
                        Back to dashboard
                    </Button>
                </div>
            </div>
            <Footer />
        </div>
    )
}
