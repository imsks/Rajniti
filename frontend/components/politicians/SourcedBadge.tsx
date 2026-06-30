"use client";

import { AlertTriangle, CheckCircle2, Info } from "lucide-react";

import type { Politician } from "@/types/politician";

type SourcedBadgeData = Pick<
  Politician,
  "sourced_pct" | "cited_fields_count" | "checkable_fields_count"
>;

type SourcedBand = "green" | "yellow" | "red" | "neutral";

type SourcedBadgeState =
  | { kind: "hidden" }
  | { kind: "limited"; band: "neutral"; label: string }
  | { kind: "unverified"; band: "red"; label: string }
  | {
      kind: "scored";
      band: "green" | "yellow" | "red";
      coverageLabel: "High coverage" | "Medium coverage" | "Low coverage";
      percentLabel: string;
    };

const BAND_STYLES: Record<SourcedBand, string> = {
  green:
    "border-emerald-300 bg-emerald-50 text-emerald-900 dark:border-emerald-500/40 dark:bg-emerald-500/12 dark:text-emerald-200",
  yellow:
    "border-amber-300 bg-amber-50 text-amber-900 dark:border-amber-500/40 dark:bg-amber-500/12 dark:text-amber-100",
  red:
    "border-rose-300 bg-rose-50 text-rose-900 dark:border-rose-500/40 dark:bg-rose-500/12 dark:text-rose-100",
  neutral:
    "border-slate-300 bg-slate-100 text-slate-900 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100",
};

export function getSourcedBadgeState(
  data: SourcedBadgeData,
): SourcedBadgeState {
  const total = data.checkable_fields_count;

  if (
    (total === null || total === undefined) &&
    (data.cited_fields_count === null ||
      data.cited_fields_count === undefined) &&
    (data.sourced_pct === null || data.sourced_pct === undefined)
  ) {
    return { kind: "hidden" };
  }

  if (typeof total === "number" && total < 3) {
    return { kind: "limited", band: "neutral", label: "Limited data" };
  }

  if (typeof data.sourced_pct !== "number") {
    return { kind: "hidden" };
  }

  if (data.sourced_pct <= 0) {
    return {
      kind: "unverified",
      band: "red",
      label: "Unverified — help us source this",
    };
  }

  if (data.sourced_pct >= 0.75) {
    return {
      kind: "scored",
      band: "green",
      coverageLabel: "High coverage",
      percentLabel: `${Math.round(data.sourced_pct * 100)}% sourced`,
    };
  }

  if (data.sourced_pct >= 0.6) {
    return {
      kind: "scored",
      band: "yellow",
      coverageLabel: "Medium coverage",
      percentLabel: `${Math.round(data.sourced_pct * 100)}% sourced`,
    };
  }

  return {
    kind: "scored",
    band: "red",
    coverageLabel: "Low coverage",
    percentLabel: `${Math.round(data.sourced_pct * 100)}% sourced`,
  };
}

export default function SourcedBadge({ politician }: { politician: SourcedBadgeData }) {
  const state = getSourcedBadgeState(politician);

  if (state.kind === "hidden") {
    return null;
  }

  const icon =
    state.kind === "scored" && state.band === "green" ? (
      <CheckCircle2 className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
    ) : state.kind === "limited" ? (
      <Info className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
    ) : (
      <AlertTriangle className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
    );

  const label =
    state.kind === "scored"
      ? `${state.coverageLabel} · ${state.percentLabel}`
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
      {icon}
      <span>{label}</span>
    </span>
  );
}
