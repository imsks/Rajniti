"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { Share2, Check, AlertTriangle } from "lucide-react";
import {
  getPoliticianProfileHref,
  getParty,
  toTitleCase,
} from "@/lib/politicianUtils";
import {
  getPartyColor,
  getPartyAcronym,
  getPartyLogo,
} from "@/lib/constants/partyColors";
import RoleBadge from "@/components/politicians/RoleBadge";
import type { Politician } from "@/types/politician";

interface PublicPoliticianCardProps {
  politician: Politician;
}

function getInitials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? "")
    .join("");
}

export default function PublicPoliticianCard({
  politician,
}: PublicPoliticianCardProps) {
  const rawParty = getParty(politician);
  const party = rawParty !== "—" ? rawParty : null;
  const partyColor = getPartyColor(party);
  const partyLogo = getPartyLogo(party);
  const href = getPoliticianProfileHref(politician);
  const initials = getInitials(politician.name);

  const [imgError, setImgError] = useState(false);
  const [logoError, setLogoError] = useState(false);
  const [shareState, setShareState] = useState<"idle" | "copied" | "error">(
    "idle",
  );
  const shareTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (shareTimerRef.current) clearTimeout(shareTimerRef.current);
    };
  }, []);

  const handleShare = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (shareTimerRef.current) clearTimeout(shareTimerRef.current);

    const name = toTitleCase(politician.name);
    const constituency = toTitleCase(politician.constituency);
    const profileUrl =
      typeof window !== "undefined" ? `${window.location.origin}${href}` : href;
    const partyPart = party ? `${party} ` : "";
    const shareText = `📍 ${name} represents ${constituency} as ${partyPart}${politician.type}.\nKnow your representative → ${profileUrl}`;

    try {
      if (typeof navigator !== "undefined" && navigator.share) {
        await navigator.share({
          title: `${name} on Rajniti`,
          text: shareText,
          url: profileUrl,
        });
      } else {
        await navigator.clipboard.writeText(shareText);
        setShareState("copied");
        shareTimerRef.current = setTimeout(() => setShareState("idle"), 2000);
      }
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") return;
      setShareState("error");
      shareTimerRef.current = setTimeout(() => setShareState("idle"), 2000);
    }
  };

  return (
    <article
      className="mt-4 group relative flex flex-col rounded-xl border-[0.5px] border-gray-200 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-500 bg-white dark:bg-gray-900 transition-colors"
      style={{
        height: "145px",
        borderTop: `3px solid ${partyColor.text}`,
        padding: "1.25rem 1.25rem 1rem",
      }}
    >
      {/* Stretched link — makes the whole card clickable without nesting a button in an anchor */}
      <Link
        href={href}
        aria-label={toTitleCase(politician.name)}
        className="absolute inset-0 z-0 rounded-xl"
      />

      {/* Top section — avatar + text. pointer-events-none so clicks fall through to the link. */}
      <div className="relative z-10 flex items-start gap-[14px] pointer-events-none">
        {/* Avatar — neutral fallback with initials */}
        <div className="shrink-0 w-[46px] h-[46px] rounded-full overflow-hidden flex items-center justify-center bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 text-sm font-semibold">
          {politician.photo && !imgError ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={politician.photo}
              alt={politician.name}
              className="w-full h-full object-cover"
              loading="lazy"
              onError={() => setImgError(true)}
            />
          ) : (
            <span aria-hidden="true">{initials}</span>
          )}
        </div>

        {/* Text block — name + constituency in tight top-down flow (4px gap, no auto margins) */}
        <div className="min-w-0 flex-1 flex flex-col gap-1">
          {/* Name row — name takes available width, pill stays flush-right & top-aligned */}
          <div className="flex items-start justify-between gap-2">
            <h2 className="flex-1 min-w-0 font-medium text-gray-900 dark:text-white leading-[1.4] line-clamp-2 group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">
              {toTitleCase(politician.name)}
            </h2>
            <RoleBadge type={politician.type} />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
            {toTitleCase(politician.constituency)}, {politician.state}
          </p>
        </div>
      </div>

      {/* Footer — mt-auto pins it to the bottom regardless of 1- or 2-line names */}
      <div className="relative z-10 mt-auto flex items-center justify-between gap-2 pointer-events-none">
        {/* Left group: party logo + party name (truncates if needed) */}
        <div className="flex items-center gap-2 flex-1 min-w-0">
          {partyLogo && !logoError && (
            <span className="inline-flex shrink-0 w-5.5 h-5.5 rounded-[6px] bg-white items-center justify-center p-[2px]">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={partyLogo}
                alt=""
                className="w-full h-full object-contain"
                loading="lazy"
                onError={() => setLogoError(true)}
              />
            </span>
          )}
          {party && (
            <span
              className="text-xs font-bold truncate"
              style={{ color: partyColor.text }}
            >
              {getPartyAcronym(party)}
            </span>
          )}
        </div>

        {/* Right group: actions row — only Share for now; star/save & compare can be
            added here later. flex-shrink-0 so the party name never compresses it. */}
        <div className="flex items-center gap-1 shrink-0 pointer-events-auto">
          <button
            onClick={handleShare}
            aria-label={
              shareState === "copied"
                ? "Link copied to clipboard"
                : shareState === "error"
                  ? "Failed to copy — try again"
                  : "Share this politician"
            }
            className={`w-[30px] h-[30px] rounded-full flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-orange-300 dark:focus:ring-orange-600 cursor-pointer ${
              shareState === "copied"
                ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
                : shareState === "error"
                  ? "bg-red-100 text-red-600 dark:bg-red-900/40 dark:text-red-300"
                  : "bg-orange-100 dark:bg-orange-600/30 hover:bg-orange-600/80 text-orange-500 dark:hover:bg-orange-600 hover:text-white transition-colors"
            }`}
          >
            {shareState === "copied" ? (
              <Check size={14} className="stroke-2" />
            ) : shareState === "error" ? (
              <AlertTriangle size={14} className="stroke-2" />
            ) : (
              <Share2 size={14} className="stroke-2" />
            )}
          </button>
        </div>
      </div>
    </article>
  );
}
