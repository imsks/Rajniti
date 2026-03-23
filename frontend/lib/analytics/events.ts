/**
 * Centralized event taxonomy for Google Analytics 4.
 *
 * Every trackable user action maps to a key here. Adding a new event is a
 * two-step process: define its payload shape below, then call
 * `trackEvent('<name>', { ... })` from any component via the useAnalytics hook.
 */

export type AnalyticsEventMap = {
  // ── Navigation ─────────────────────────────────────────────────────────
  nav_click: {
    link_text: string
    link_url: string
    nav_section: "navbar" | "footer" | "user_menu"
  }

  // ── Authentication ─────────────────────────────────────────────────────
  login_start: {
    method: "google"
    trigger_location: string
  }
  logout: Record<string, never>

  // ── Search & Discovery ─────────────────────────────────────────────────
  search: {
    search_term: string
    results_count?: number
    search_location: "dashboard" | "my_politicians"
  }

  filter_apply: {
    filter_type: "tab" | "state" | "party" | "items_per_page"
    filter_value: string
  }

  filter_clear: Record<string, never>

  // ── Politician Interactions ────────────────────────────────────────────
  politician_card_click: {
    politician_id: string
    politician_name: string
    politician_type: "MP" | "MLA"
    party: string
    state: string
  }

  politician_profile_view: {
    politician_id: string
    politician_name: string
    politician_type: "MP" | "MLA"
    party: string
    state: string
    constituency: string
    // Optional because older URLs are UUID-based (no slug), and new URLs can
    // carry only a slug or slug+short-id disambiguator.
    route_slug?: string | null
    route_uuid_short?: string | null
  }

  my_politician_set: {
    politician_id: string
    politician_name: string
    slot_type: "MP" | "MLA"
  }

  my_politician_remove: {
    slot_type: "MP" | "MLA"
  }

  // ── Onboarding ─────────────────────────────────────────────────────────
  onboarding_step_complete: {
    step: number
    step_name: string
  }

  onboarding_complete: {
    political_interest: string
  }

  onboarding_skip: {
    at_step: number
  }

  // ── Profile ────────────────────────────────────────────────────────────
  profile_update_submit: Record<string, never>
  profile_update_success: Record<string, never>
  profile_update_error: {
    error_message: string
  }

  // ── Engagement / CTAs ──────────────────────────────────────────────────
  cta_click: {
    cta_name: string
    cta_url?: string
    page_location: string
  }

  external_link_click: {
    link_text: string
    link_url: string
    page_location: string
  }

  contribute_click: {
    contribute_type: "data" | "code" | "info" | "bug"
    politician_id?: string
    page_location: string
  }

  // ── Location ───────────────────────────────────────────────────────────
  location_lookup: {
    method: "gps" | "pincode"
    success: boolean
  }

  // ── Pagination ─────────────────────────────────────────────────────────
  pagination: {
    direction: "next" | "previous"
    page_number: number
    total_pages: number
  }

  // ── Errors ─────────────────────────────────────────────────────────────
  error_view: {
    error_type: "api" | "not_found" | "connection"
    error_message: string
    page_location: string
  }
}

export type AnalyticsEvent = keyof AnalyticsEventMap
