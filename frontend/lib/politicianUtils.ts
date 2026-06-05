import type { Politician } from "@/types/politician";

/**
 * Converts ALL-CAPS politician names to Title Case.
 * Words that contain dots (abbreviations like "B.J.P.") are kept as-is.
 * Leading/trailing parentheses are preserved around the title-cased word.
 *
 * Examples:
 *   "NARENDRA MODI"            → "Narendra Modi"
 *   "BHUPATHI RAJU (B.J.P.VARMA)" → "Bhupathi Raju (B.J.P.VARMA)"
 */
export function toTitleCase(name: string): string {
  if (!name) return name;

  return name
    .trim()
    .split(/\s+/)
    .map((word) => {
      const leading = word.match(/^\(*/)![0];
      const trailing = word.match(/\)*$/)![0];

      const core = word.slice(leading.length, word.length - trailing.length);

      if (!core) return word;

      // Handle names like C.M.RAMESH or B.J.P.VARMA
      const abbrMatch = core.match(/^((?:[A-Z]\.)+)([A-Z]+)$/);

      if (abbrMatch) {
        const [, abbr, surname] = abbrMatch;
        return (
          leading +
          abbr +
          " " +
          surname.charAt(0).toUpperCase() +
          surname.slice(1).toLowerCase() +
          trailing
        );
      }

      return (
        leading +
        core.charAt(0).toUpperCase() +
        core.slice(1).toLowerCase() +
        trailing
      );
    })
    .join(" ");
}

/** Path segment for `/politician/[slug]` — prefers API slug, falls back to id. */
export function getPoliticianProfileSegment(p: Politician): string {
  const slug = p.slug?.trim();
  if (slug) return slug;
  return p.id;
}

/** Full href for a politician profile (slug when available). */
export function getPoliticianProfileHref(p: Politician): string {
  return `/politician/${encodeURIComponent(getPoliticianProfileSegment(p))}`;
}

/** Pure: get the latest (first) party name from political background. */
export function getParty(p: Politician): string {
  const elections = p.political_background?.elections ?? [];
  return elections.length > 0 ? elections[0].party : "—";
}

/** Pure: short party abbreviation for avatar. */
export function getPartyInitial(p: Politician): string {
  const party = getParty(p);
  if (party === "—") return "?";
  const words = party.split(" ").filter((w) => w.length > 2);
  return words
    .slice(0, 3)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}
