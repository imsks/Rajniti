import Link from "next/link";
import {
  buildPoliticiansPath,
  type PoliticiansListFilters,
} from "@/lib/politicians/directory";

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
  if (totalPages <= 1) return null;

  const prevPath = page > 1 ? buildPoliticiansPath(page - 1, filters) : null;
  const nextPath =
    page < totalPages ? buildPoliticiansPath(page + 1, filters) : null;

  return (
    <nav
      className="flex items-center justify-between mt-8 pt-6 border-t border-orange-100 dark:border-gray-700"
      aria-label="Pagination"
    >
      {prevPath ? (
        <Link
          href={prevPath}
          className="px-4 py-2 rounded-lg border border-orange-200 dark:border-gray-600 text-orange-700 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-gray-800 transition"
        >
          Previous
        </Link>
      ) : (
        <span />
      )}
      <span className="text-sm text-gray-600 dark:text-gray-400">
        Page {page} of {totalPages}
      </span>
      {nextPath ? (
        <Link
          href={nextPath}
          className="px-4 py-2 rounded-lg border border-orange-200 dark:border-gray-600 text-orange-700 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-gray-800 transition"
        >
          Next
        </Link>
      ) : (
        <span />
      )}
    </nav>
  );
}
