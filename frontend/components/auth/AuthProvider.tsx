'use client'

import { useEffect, useRef } from 'react'
import { SessionProvider, useSession } from 'next-auth/react'
import { useAnalytics } from '@/hooks/useAnalytics'

/**
 * sessionStorage key written by login_start (signin page + UserButton).
 * Stores the trigger_location so login_success can report it.
 * Cleared once login_success fires so it only fires once per sign-in flow.
 */
export const LOGIN_INTENT_KEY = 'rajniti_login_intent'

/**
 * Invisible observer that sits inside the SessionProvider.
 * Watches for the session status transitioning to 'authenticated' while a
 * login_intent flag is present in sessionStorage — meaning the user just
 * completed OAuth in this tab, not a pre-existing session on page load.
 */
function AuthAnalyticsObserver() {
  const { status } = useSession()
  const { trackEvent } = useAnalytics()
  const firedRef = useRef(false)

  useEffect(() => {
    if (status !== 'authenticated' || firedRef.current) return

    const intent = sessionStorage.getItem(LOGIN_INTENT_KEY)
    if (!intent) return // already-authenticated user loading a new page — skip

    firedRef.current = true
    sessionStorage.removeItem(LOGIN_INTENT_KEY)

    trackEvent('login_success', {
      method: 'google',
      trigger_location: intent,
    })
  }, [status, trackEvent])

  return null
}

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <AuthAnalyticsObserver />
      {children}
    </SessionProvider>
  )
}
