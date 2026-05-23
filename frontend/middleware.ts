import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { withAuth } from "next-auth/middleware"
import { resolvePoliticianCanonicalRedirect } from "@/lib/seo/middleware-canonical"

export default withAuth(
    async function middleware(req: NextRequest) {
        const redirect = await resolvePoliticianCanonicalRedirect(req)
        if (redirect) return redirect
        return NextResponse.next()
    },
    {
        callbacks: {
            authorized: ({ token, req }) => {
                const path = req.nextUrl.pathname
                if (path.startsWith("/politician/")) return true
                return !!token
            },
        },
    }
)

export const config = {
    matcher: [
        "/politician/:path*",
        "/dashboard/:path*",
        "/onboarding",
        "/profile/:path*",
    ],
}
