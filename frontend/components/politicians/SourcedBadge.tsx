"use client";

import { AlertCircle, AlertTriangle, CheckCircle2, Info, ShieldAlert } from "lucide-react";

import type { Politician } from "@/types/politician";

type SourcedBadgeData = Pick<
  Politician,
  | "sourced_pct"
  | "cited_fields_count"
  | "checkable_fields_count"
  | "categories_mostly_present"
>;

type SourcedBand = "green" | "yellow" | "red" | "blue";

type SourcedBadgeState =
  | { kind: "limited"; band: "blue"; label: string }
  | { kind: "unverified"; band: "red"; label: string }
  | {
      kind: "scored";
      band: "green" | "yellow" | "red";
      coverageWord: "High" | "Medium" | "Low";
      percentLabel: string;
    };

const BAND_STYLES: Record<SourcedBand, string> = {
  green:
    "border-emerald-300 bg-emerald-50 text-emerald-900 dark:border-emerald-500/40 dark:bg-emerald-500/12 dark:text-emerald-200",
  yellow:
    "border-amber-300 bg-amber-50 text-amber-900 dark:border-amber-500/40 dark:bg-amber-500/12 dark:text-amber-100",
  red:
    "border-rose-300 bg-rose-50 text-rose-900 dark:border-rose-500/40 dark:bg-rose-500/12 dark:text-rose-100",
  blue:
    "border-blue-300 bg-blue-50 text-blue-900 dark:border-blue-500/40 dark:bg-blue-500/12 dark:text-blue-100",
};

/**
 * Every politician profile always shows a badge — there is no hidden state.
 *
 * A percentage only appears once the profile is broadly filled in (all but
 * at most one of education, history, family, criminal, contact, and
 * performance-when-applicable has data) AND there are 5+ checkable fields
 * overall. Genuine zero coverage (data exists, none of it cited) always
 * renders as "Unverified", regardless of how many categories are filled in —
 * a single uncited fact, or every category with exactly one uncited fact,
 * are both "Unverified". Anything else that's incomplete (too many missing
 * categories, or cited but too thin) falls back to "Limited data".
 */
export function getSourcedBadgeState(
  data: SourcedBadgeData,
): SourcedBadgeState {
  const total = data.checkable_fields_count;
  const cited = data.cited_fields_count;

  if (typeof total !== "number" || total === 0) {
    return { kind: "limited", band: "blue", label: "Limited data" };
  }

  if (typeof cited !== "number" || cited === 0) {
    return {
      kind: "unverified",
      band: "red",
      label: "Unverified — help us source this",
    };
  }

  if (!data.categories_mostly_present || total < 5 || typeof data.sourced_pct !== "number") {
    return { kind: "limited", band: "blue", label: "Limited data" };
  }

  const pct = data.sourced_pct;
  const percentLabel = `${Math.round(pct * 100)}% verified`;

  if (pct >= 0.75) {
    return { kind: "scored", band: "green", coverageWord: "High", percentLabel };
  }

  if (pct >= 0.6) {
    return { kind: "scored", band: "yellow", coverageWord: "Medium", percentLabel };
  }

  return { kind: "scored", band: "red", coverageWord: "Low", percentLabel };
}

export default function SourcedBadge({ politician }: { politician: SourcedBadgeData }) {
  const state = getSourcedBadgeState(politician);

  const Icon =
    state.kind === "limited"
      ? Info
      : state.kind === "unverified"
        ? ShieldAlert
        : state.band === "green"
          ? CheckCircle2
          : state.band === "yellow"
            ? AlertCircle
            : AlertTriangle;

  const label =
    state.kind === "scored"
      ? `${state.percentLabel} · ${state.coverageWord}`
      : state.label;

  const title =
    typeof politician.checkable_fields_count === "number" &&
    typeof politician.cited_fields_count === "number"
      ? `${politician.cited_fields_count} of ${politician.checkable_fields_count} checkable fields carry citations`
      : undefined;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${BAND_STYLES[state.band]}`}
      data-sourced-band={state.band}
      data-sourced-state={state.kind}
      title={title}
    >
      <Icon className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
      <span>{label}</span>
    </span>
  );
}
