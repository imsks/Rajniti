import { withAuth } from 'next-auth/middleware'
import { NextResponse } from 'next/server'
import { ROUTES } from '@/lib/routes'

export default withAuth(
  function middleware(req) {
    const { pathname } = req.nextUrl
    const token = req.nextauth.token

    const onboardingCompleted = token?.onboardingCompleted ?? false

    if (!onboardingCompleted && pathname.startsWith(ROUTES.dashboard)) {
      return NextResponse.redirect(new URL(ROUTES.onboarding, req.url))
    }

    if (onboardingCompleted && pathname === ROUTES.onboarding) {
      return NextResponse.redirect(new URL(ROUTES.dashboard, req.url))
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
