import { withAuth } from 'next-auth/middleware'
import { NextResponse } from 'next/server'

export default withAuth(
  function middleware(req) {
    const { pathname } = req.nextUrl
    const token = req.nextauth.token

    // ✅ SAFE DEFAULT
    const onboardingCompleted = token?.onboardingCompleted ?? false

    console.log("🔥 Middleware:", {
      path: pathname,
      onboardingCompleted
    })

    // 🚀 Not onboarded → force onboarding
    if (!onboardingCompleted && pathname.startsWith('/dashboard')) {
      return NextResponse.redirect(new URL('/onboarding', req.url))
    }

    // 🚀 Already onboarded → skip onboarding
    if (onboardingCompleted && pathname === '/onboarding') {
      return NextResponse.redirect(new URL('/dashboard', req.url))
    }

    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token
    }
  }
)

export const config = {
  matcher: ['/dashboard/:path*', '/onboarding', '/profile/:path*'],
}