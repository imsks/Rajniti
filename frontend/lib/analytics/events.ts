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
  /** User views the /auth/signin page (may not click anything). */
  signin_page_view: {
    /** How they arrived — direct URL, redirect from a protected page, etc. */
    referrer: string
  }

  /** User clicks a "Sign In" button anywhere on the site. */
  login_start: {
    method: "google"
    trigger_location: string
  }

  /**
   * Google OAuth completed and NextAuth created a session.
   * Fired once per sign-in flow using a sessionStorage flag set by login_start.
   * This event lets you calculate the true sign-in conversion rate:
   *   login_success / login_start
   */
  login_success: {
    method: "google"
    /** Where the sign-in was originally triggered */
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

  /**
   * User clicked "Back" inside onboarding — a soft drop-off signal.
   * Repeated back-clicks on the same step may indicate confusion.
   */
  onboarding_back_click: {
    step: number
    step_name: string
  }

  /**
   * User left the onboarding page before completing it via SPA navigation
   * (clicking a link, browser back within the app, etc.).
   * Fired on React component unmount. Does NOT fire when the tab/window closes —
   * that is captured by onboarding_tab_close instead.
   */
  onboarding_abandoned: {
    last_step: number
    last_step_name: string
  }

  /**
   * User closed the tab, closed the browser window, refreshed the page, or
   * typed a new URL while onboarding was incomplete.
   * Fired via the `pagehide` event with beacon transport so the hit is
   * delivered even as the browser tears down the page.
   */
  onboarding_tab_close: {
    last_step: number
    last_step_name: string
  }

  /**
   * User clicks "Complete Onboarding 🚀" — fires before the API call.
   * Compare with onboarding_complete to spot API-failure drop-off.
   */
  onboarding_submit_click: Record<string, never>

  onboarding_complete: {
    political_ideology: string
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

  // ── Scroll Depth ───────────────────────────────────────────────────────
  /**
   * Fired when the user scrolls to a milestone (25 / 50 / 75 / 90 %).
   * Each milestone fires at most once per page load.
   */
  scroll_depth: {
    depth_percent: 25 | 50 | 75 | 90
    page_location: string
    /** Politician ID when on a profile page */
    politician_id?: string
  }

  // ── Section Visibility ─────────────────────────────────────────────────
  /**
   * Fired (once) the first time a politician-profile section enters the viewport.
   * Tells us which sections users actually read vs. scroll past.
   */
  section_view: {
    section_name:
      | "political_history"
      | "performance"
      | "education"
      | "family"
      | "criminal_records"
      | "contact"
      | "contribute_cta"
    politician_id: string
    politician_name: string
  }

  // ── Engagement Time ────────────────────────────────────────────────────
  /**
   * Fired on component unmount — tells us how long users spent on a page.
   * Useful for measuring depth of engagement with politician profiles.
   */
  time_on_page: {
    duration_seconds: number
    page_location: string
    politician_id?: string
  }

  // ── UI Preferences ─────────────────────────────────────────────────────
  /** Fired when the user clicks the light/dark mode toggle. */
  theme_toggle: {
    new_theme: "light" | "dark"
  }

  // ── Politician Profile Actions ─────────────────────────────────────────
  /**
   * Fired when a user shares a politician profile.
   * method: "native_share" = OS share sheet (mobile), "clipboard" = copied link (desktop).
   */
  profile_share: {
    method: "native_share" | "clipboard"
    politician_id: string
    politician_name: string
  }

  /**
   * Fired when a user clicks a section tab on a politician profile.
   * Tells us which sections users actively navigate to.
   */
  profile_tab_click: {
    tab_name: "performance" | "criminal" | "history" | "education" | "family" | "contact"
    politician_id: string
    politician_name: string
  }

  /**
   * Fired when a user expands or collapses a "Show X more" section.
   * Tells us whether users want to see more data in a given section.
   */
  section_expand: {
    section: "criminal_records" | "education"
    action: "expand" | "collapse"
    politician_id: string
  }

  // ── Citation & Data Quality ────────────────────────────────────────────
  /**
   * Fired when a user clicks a citation source link on a politician profile.
   * Tells us which sections have the most trusted/checked data.
   */
  citation_link_click: {
    /** Section label passed to <CitationLink label="…"> */
    citation_label: string
    /** Source name from the citation object */
    source: string
    /** The destination URL */
    url: string
  }

  /**
   * Fired when a user clicks "Report Inaccuracy" on a politician profile.
   * A leading indicator of data quality issues.
   */
  report_inaccuracy_click: {
    politician_id: string
    politician_name: string
  }

  // ── Errors ─────────────────────────────────────────────────────────────
  error_view: {
    error_type: "api" | "not_found" | "connection"
    error_message: string
    page_location: string
  }
}

export type AnalyticsEvent = keyof AnalyticsEventMap
