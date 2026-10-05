"use client"

import { useCallback } from "react"
import { useAnalytics } from "./useAnalytics"
import { buildSaranshUrl, type SaranshPlacement } from "@/lib/constants/saransh"

export interface SaranshLinkProps {
  href: string
  onClick: () => void
  onAuxClick: (event: { button: number }) => void
}

/**
 * Returns a factory for the props every outbound Saransh link needs: an
 * attributed URL plus `saransh_click` tracking.
 *
 * `onAuxClick` counts middle-click new-tab opens, which never fire `click`.
 * Ctrl/cmd-click does fire a regular `click`, so it is already counted.
 */
export function useSaranshLink() {
  const { trackEvent } = useAnalytics()

  return useCallback(
    (placement: SaranshPlacement, pageLocation: string): SaranshLinkProps => {
      const href = buildSaranshUrl(placement)

      const track = () =>
        trackEvent("saransh_click", {
          link_url: href,
          page_location: pageLocation,
          placement,
        })

      return {
        href,
        onClick: track,
        onAuxClick: (event: { button: number }) => {
          if (event.button === 1) track()
        },
      }
    },
    [trackEvent]
  )
}
