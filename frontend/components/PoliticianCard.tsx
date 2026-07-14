"use client";

import Link from "next/link";
import { m } from "framer-motion";
import { Avatar, Badge } from "@sutra_ui/ui";
import Text from "@/components/ui/Text";
import RoleBadge from "@/components/politicians/RoleBadge";
import NextImage from "next/image";
import { useAnalytics } from "@/hooks/useAnalytics";
import { getPoliticianProfileHref, toTitleCase } from "@/lib/politicianUtils";
import type { Politician } from "@/types/politician";

interface PoliticianCardProps {
  politician: Politician;
}

/** Get the latest (first) party name from political background */
function getParty(p: Politician): string {
  const elections = p.political_background?.elections ?? [];
  return elections.length > 0 ? elections[0].party : "—";
}

/** Check if politician was updated in the last 7 days */
// function isRecentlyUpdated(isoString: string | null | undefined): boolean {
//   if (!isoString) return false;

//   try {
//     const date = new Date(isoString);
//     const now = new Date();
//     const diffMs = now.getTime() - date.getTime();
//     const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
//     return diffDays <= 7 && diffDays >= 0;
//   } catch {
//     return false;
//   }
// }

export default function PoliticianCard({ politician }: PoliticianCardProps) {
  const party = getParty(politician);
  const hasPhoto = !!politician.photo;
  // const recentlyUpdated = isRecentlyUpdated(politician.updated_at);
  const { trackEvent } = useAnalytics();
  return (
    <Link
      href={getPoliticianProfileHref(politician)}
      className="block group"
      onClick={() =>
        trackEvent("politician_card_click", {
          politician_id: politician.id,
          politician_name: politician.name,
          politician_type: politician.type as "MP" | "MLA",
          party,
          state: politician.state,
        })
      }
    >
      <m.div
        whileHover={{ y: -4, scale: 1.02 }}
        transition={{ duration: 0.2 }}
        className="bg-surface rounded-2xl shadow-sm border border-border p-5 hover:border-accent hover:shadow-lg transition-all h-full flex flex-col"
      >
        {/* Top: Photo / Avatar + Name + Badges */}
        <div className="flex items-start gap-4 mb-3">
          <Avatar
            src={hasPhoto ? politician.photo! : undefined}
            name={politician.name}
            className="w-14 h-14 shrink-0 border-2 border-accent-subtle"
          />

          <div className="flex-1 min-w-0">
            <Text
              variant="body"
              weight="bold"
              className="truncate"
            >
              {toTitleCase(politician.name)}
            </Text>
            <Text variant="small" color="muted" className="truncate">
              {party}
            </Text>
          </div>

          {/* Type badge */}
          <RoleBadge type={politician.type} />
        </div>

        {/* Info pills */}
        <div className="flex flex-wrap gap-2 mb-3">
          <Badge variant="neutral" tone="subtle" size="sm" className="rounded-lg">
            <NextImage
              src="/logo/location.svg"
              alt="Constituency"
              width={16}
              height={16}
              className="w-4 h-4 dark:filter-[invert(0.70)_brightness(1.2)]"
            />{" "}
            {politician.constituency}
          </Badge>
          <Badge variant="neutral" tone="subtle" size="sm" className="rounded-lg">
            <NextImage
              src="/logo/skyline.svg"
              alt="State"
              width={16}
              height={16}
              className="w-4 h-4 dark:filter-[invert(0.70)_brightness(1.2)]"
            />{" "}
            {politician.state}
          </Badge>
        </div>

        {/* CTA Button - Always visible */}
        <div className="mt-auto pt-3 border-t border-border">
          <div className="flex items-center justify-between text-accent group-hover:text-accent-hover transition-colors">
            <Text variant="small" weight="semibold" color="primary">
              View Details
            </Text>
            <span className="transform group-hover:translate-x-1 transition-transform">
              →
            </span>
          </div>
        </div>
      </m.div>
    </Link>
  );
}
