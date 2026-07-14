"use client";

import { m } from "framer-motion";
import { Avatar, Badge } from "@sutra_ui/ui";
import Text from "@/components/ui/Text";
import Button from "@/components/ui/Button";
import RoleBadge from "@/components/politicians/RoleBadge";
import { getPoliticianProfileHref } from "@/lib/politicianUtils";
import type { Politician, ElectionType } from "@/types/politician";
interface MyPoliticianCardProps {
  politician: Politician | null;
  slotType: ElectionType;
  onAddClick?: () => void;
  onRemove?: () => void;
}

const SLOT_LABELS: Record<ElectionType, string> = {
  MP: "Your MP",
  MLA: "Your MLA",
};

export default function MyPoliticianCard({
  politician,
  slotType,
  onAddClick,
  onRemove,
}: MyPoliticianCardProps) {
  const label = SLOT_LABELS[slotType];
  const isPlaceholder = politician === null;

  if (isPlaceholder) {
    return (
      <m.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-surface/70 rounded-2xl shadow-sm border-2 border-dashed border-accent-subtle p-6 flex flex-col items-center justify-center min-h-[200px]"
      >
        <Text variant="body" color="muted" className="mb-2">
          {label}
        </Text>
        <Text variant="small" color="muted" className="mb-4 text-center">
          Search above to add
        </Text>
        {onAddClick && (
          <Button
            variant="outline"
            size="sm"
            onClick={onAddClick}
            leftIcon={<span className="text-lg">+</span>}
          >
            Add
          </Button>
        )}
      </m.div>
    );
  }

  const hasPhoto = !!politician.photo;
  const designation =
    politician.type === "MP"
      ? `MP of ${politician.constituency}`
      : `MLA of ${politician.constituency}`;

  return (
    <m.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-surface rounded-xl shadow-md border border-border p-5 hover:border-accent hover:shadow-lg transition-all h-full flex flex-col"
    >
      <div className="flex items-start gap-4 mb-3">
        <Avatar
          src={hasPhoto ? politician.photo! : undefined}
          name={politician.name}
          className="w-14 h-14 shrink-0 border-2 border-accent-subtle"
        />
        <div className="flex-1 min-w-0">
          <Text variant="body" weight="bold" className="truncate">
            {politician.name}
          </Text>
          <Text variant="small" color="muted" className="truncate">
            {designation}
          </Text>
        </div>
        <RoleBadge type={politician.type} />
      </div>
      <div className="flex flex-wrap gap-2 mb-4">
        <Badge variant="neutral" tone="subtle" size="sm" className="rounded-lg">
          {politician.type}
        </Badge>
        <Badge variant="neutral" tone="subtle" size="sm" className="rounded-lg">
          {politician.constituency}
        </Badge>
      </div>
      <div className="mt-auto pt-3 border-t border-border flex flex-wrap items-center justify-between gap-2">
        <Button
          href={getPoliticianProfileHref(politician)}
          variant="primary"
          size="sm"
          className="w-full sm:w-auto"
        >
          View more
        </Button>
        {onRemove && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.preventDefault();
              onRemove();
            }}
            className="text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 p-2 min-w-0"
            aria-label="Remove from your politicians"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </Button>
        )}
      </div>
    </m.div>
  );
}
