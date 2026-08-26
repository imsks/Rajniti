import { getSiteUrl } from "@/lib/seo/site";
import Pagination from "@/components/ui/Pagination";

export const PER_PAGE = 48;

export interface PoliticiansListFilters {
  type?: "MP" | "MLA";
  state?: string;
  stateSlug?: string;
  q?: string;
  /** Selected party names (full names as returned by /parties). */
  parties?: string[];
}

export function buildPoliticiansPath(
  page: number,
  filters: PoliticiansListFilters = {},
): string {
  const { type, stateSlug, q, parties } = filters;

  // Type owns the path; state composes as a query param so both can apply at once.
  // State alone keeps its canonical /state/<slug> route for SEO.
  let base = "/politicians";
  const params = new URLSearchParams();
  if (type === "MP") {
    base = "/politicians/mp";
    if (stateSlug) params.set("state", stateSlug);
  } else if (type === "MLA") {
    base = "/politicians/mla";
    if (stateSlug) params.set("state", stateSlug);
  } else if (stateSlug) {
    base = `/politicians/state/${encodeURIComponent(stateSlug)}`;
  }

  if (page > 1) base = `${base}/page/${page}`;

  if (q?.trim()) params.set("q", q.trim());
  if (parties && parties.length > 0) params.set("party", parties.join(","));
  const qs = params.toString();
  return qs ? `${base}?${qs}` : base;
}

/** Parse the `party` query param (comma-separated) into an array of party names. */
export function parsePartyParam(party?: string): string[] | undefined {
  if (!party) return undefined
  const list = party
    .split(",")
    .map((p) => p.trim())
    .filter(Boolean)
  return list.length > 0 ? list : undefined
}

export function buildPoliticiansTitle(
  filters: PoliticiansListFilters,
  page: number,
): string {
  let title = "All Indian MPs & MLAs";
  if (filters.type === "MP") title = "Lok Sabha MPs";
  else if (filters.type === "MLA") title = "Vidhan Sabha MLAs";
  else if (filters.state) title = `${filters.state} MPs & MLAs`;
  // Note: We intentionally do NOT change the visible H1 for search queries.
  // The H1 stays canonical (e.g., "All Indian MPs & MLAs") while a separate
  // "Showing X results for <query>" line appears below the filters.
  if (page > 1) title = `${title} — Page ${page}`;
  return title;
}

/**
 * Build the "Showing X results for "<query>"" line when a search is active.
 * Returns null if no search query is present.
 */
export function buildSearchResultsLine(
  query: string | undefined,
  total: number,
): string | null {
  const trimmed = query?.trim();
  if (!trimmed) return null;
  const countText = total === 1 ? "1 result" : `${total.toLocaleString()} results`;
  return `Showing ${countText} for "${trimmed}"`;
}

export function buildPoliticiansDescription(
  filters: PoliticiansListFilters,
): string {
  if (filters.type === "MP") {
    return "Browse all Lok Sabha Members of Parliament in India — constituency, state, and party on Rajniti.";
  }
  if (filters.type === "MLA") {
    return "Browse all Vidhan Sabha Members of Legislative Assembly in India — constituency, state, and party on Rajniti.";
  }
  if (filters.state) {
    return `Browse MPs and MLAs from ${filters.state} — profiles, party affiliation, and constituency details on Rajniti.`;
  }
  return "Browse all Indian MPs and MLAs — search by name, filter by state or type. Open data on Rajniti.";
}

interface PoliticiansPaginationProps {
  page: number;
  totalPages: number;
  filters: PoliticiansListFilters;
}

export function PoliticiansPagination({
  page,
  totalPages,
  filters,
}: PoliticiansPaginationProps) {
  return (
    <Pagination
      currentPage={page}
      totalPages={totalPages}
      buildHref={(p) => buildPoliticiansPath(p, filters)}
    />
  );
}

export function getPaginationAlternates(
  page: number,
  totalPages: number,
  filters: PoliticiansListFilters,
): { prev?: string; next?: string } {
  const base = getSiteUrl();
  const result: { prev?: string; next?: string } = {};
  if (page > 1) {
    result.prev = `${base}${buildPoliticiansPath(page - 1, filters)}`;
  }
  if (page < totalPages) {
    result.next = `${base}${buildPoliticiansPath(page + 1, filters)}`;
  }
  return result;
}
