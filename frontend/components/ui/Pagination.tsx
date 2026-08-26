import Link from "next/link";

/**
 * Props for the Pagination component.
 *
 * Supports two modes:
 * 1. Path-based (SSR): Provide `buildHref` to generate links for SEO/SSR.
 * 2. Client-side: Provide `onPageChange` for client-side state updates.
 */
export interface PaginationProps {
  /** Current page number (1-indexed) */
  currentPage: number;
  /** Total number of pages */
  totalPages: number;
  /**
   * Function to build the href for a given page number.
   * If provided, renders anchor tags for path-based routing (SSR/SEO friendly).
   */
  buildHref?: (page: number) => string;
  /**
   * Callback when a page is clicked (client-side navigation).
   * If provided without buildHref, renders buttons instead of links.
   */
  onPageChange?: (page: number) => void;
  /** Additional CSS classes for the nav wrapper */
  className?: string;
}

/**
 * Compute the page numbers to display with ellipsis truncation.
 *
 * Algorithm:
 * - Always show page 1 and the last page
 * - Show current page ± siblingsCount
 * - Use ellipsis ('…') to collapse gaps larger than 1
 *
 * @param currentPage - Current page (1-indexed)
 * @param totalPages - Total pages
 * @param siblingsCount - Number of pages to show on each side of current (default 1 for mobile, 2 for desktop)
 * @returns Array of page numbers and '…' strings
 */
export function computePageRange(
  currentPage: number,
  totalPages: number,
  siblingsCount: number = 1
): (number | "…")[] {
  // Edge case: few pages, show all
  if (totalPages <= 1 + siblingsCount * 2 + 4) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  const leftSibling = Math.max(currentPage - siblingsCount, 1);
  const rightSibling = Math.min(currentPage + siblingsCount, totalPages);

  const showLeftEllipsis = leftSibling > 2;
  const showRightEllipsis = rightSibling < totalPages - 1;

  const pages: (number | "…")[] = [];

  // Always show page 1
  pages.push(1);

  // Left ellipsis or page 2
  if (showLeftEllipsis) {
    pages.push("…");
  } else if (leftSibling > 1) {
    // Show page 2 if no ellipsis needed
    for (let i = 2; i < leftSibling; i++) {
      pages.push(i);
    }
  }

  // Pages around current
  for (let i = leftSibling; i <= rightSibling; i++) {
    if (i !== 1 && i !== totalPages) {
      pages.push(i);
    }
  }

  // Right ellipsis or remaining pages
  if (showRightEllipsis) {
    pages.push("…");
  } else if (rightSibling < totalPages) {
    // Show remaining pages if no ellipsis needed
    for (let i = rightSibling + 1; i < totalPages; i++) {
      pages.push(i);
    }
  }

  // Always show last page
  if (totalPages > 1) {
    pages.push(totalPages);
  }

  return pages;
}

/**
 * Reusable Pagination component with numbered pages and ellipsis truncation.
 *
 * Features:
 * - Numbered pages with ellipsis (e.g., 1 … 5 6 [7] 8 9 … 90)
 * - First and last page always visible
 * - Path-based (SSR) or client-side navigation modes
 * - Active page visually distinct with `aria-current="page"`
 * - Prev/Next buttons disabled at boundaries
 * - Mobile responsive with condensed view
 * - Light and dark mode support
 * - Keyboard accessible
 */
export default function Pagination({
  currentPage,
  totalPages,
  buildHref,
  onPageChange,
  className = "",
}: PaginationProps) {
  if (totalPages <= 1) return null;

  const isFirstPage = currentPage === 1;
  const isLastPage = currentPage === totalPages;

  // Use smaller sibling count on mobile via responsive classes
  const desktopPages = computePageRange(currentPage, totalPages, 2);
  const mobilePages = computePageRange(currentPage, totalPages, 1);

  // Shared styles
  const buttonBase =
    "inline-flex items-center justify-center min-w-[44px] min-h-[44px] px-3 py-2 text-sm font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900";

  const enabledStyle =
    "border border-orange-200 dark:border-gray-600 text-orange-700 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-gray-800 bg-white dark:bg-gray-900";

  const disabledStyle =
    "border border-gray-200 dark:border-gray-700 text-gray-400 dark:text-gray-600 cursor-not-allowed bg-gray-50 dark:bg-gray-800";

  const activeStyle =
    "bg-orange-600 dark:bg-orange-500 text-white border border-orange-600 dark:border-orange-500 font-bold";

  const ellipsisStyle =
    "inline-flex items-center justify-center min-w-[44px] min-h-[44px] px-2 text-gray-500 dark:text-gray-400 cursor-default select-none";

  /**
   * Render a page button/link.
   */
  function renderPageItem(page: number | "…", index: number, isMobile: boolean) {
    if (page === "…") {
      return (
        <span
          key={`ellipsis-${index}-${isMobile ? "mobile" : "desktop"}`}
          className={ellipsisStyle}
          aria-hidden="true"
        >
          …
        </span>
      );
    }

    const isActive = page === currentPage;

    if (isActive) {
      return (
        <span
          key={page}
          className={`${buttonBase} ${activeStyle}`}
          aria-current="page"
          aria-label={`Page ${page}, current page`}
        >
          {page}
        </span>
      );
    }

    // Path-based navigation (SSR)
    if (buildHref) {
      return (
        <Link
          key={page}
          href={buildHref(page)}
          className={`${buttonBase} ${enabledStyle}`}
          aria-label={`Go to page ${page}`}
        >
          {page}
        </Link>
      );
    }

    // Client-side navigation
    return (
      <button
        key={page}
        type="button"
        onClick={() => onPageChange?.(page)}
        className={`${buttonBase} ${enabledStyle}`}
        aria-label={`Go to page ${page}`}
      >
        {page}
      </button>
    );
  }

  /**
   * Render Previous button.
   */
  function renderPrevButton() {
    const content = (
      <>
        <span aria-hidden="true">←</span>
        <span className="ml-1 hidden sm:inline">Previous</span>
      </>
    );

    if (isFirstPage) {
      return (
        <span
          className={`${buttonBase} ${disabledStyle}`}
          aria-disabled="true"
          aria-label="Previous page (disabled, already on first page)"
        >
          {content}
        </span>
      );
    }

    if (buildHref) {
      return (
        <Link
          href={buildHref(currentPage - 1)}
          className={`${buttonBase} ${enabledStyle}`}
          aria-label="Go to previous page"
        >
          {content}
        </Link>
      );
    }

    return (
      <button
        type="button"
        onClick={() => onPageChange?.(currentPage - 1)}
        className={`${buttonBase} ${enabledStyle}`}
        aria-label="Go to previous page"
      >
        {content}
      </button>
    );
  }

  /**
   * Render Next button.
   */
  function renderNextButton() {
    const content = (
      <>
        <span className="mr-1 hidden sm:inline">Next</span>
        <span aria-hidden="true">→</span>
      </>
    );

    if (isLastPage) {
      return (
        <span
          className={`${buttonBase} ${disabledStyle}`}
          aria-disabled="true"
          aria-label="Next page (disabled, already on last page)"
        >
          {content}
        </span>
      );
    }

    if (buildHref) {
      return (
        <Link
          href={buildHref(currentPage + 1)}
          className={`${buttonBase} ${enabledStyle}`}
          aria-label="Go to next page"
        >
          {content}
        </Link>
      );
    }

    return (
      <button
        type="button"
        onClick={() => onPageChange?.(currentPage + 1)}
        className={`${buttonBase} ${enabledStyle}`}
        aria-label="Go to next page"
      >
        {content}
      </button>
    );
  }

  return (
    <nav
      className={`flex flex-wrap items-center justify-center gap-1 mt-8 pt-6 border-t border-orange-100 dark:border-gray-700 ${className}`}
      aria-label="Pagination"
      role="navigation"
    >
      {renderPrevButton()}

      {/* Mobile pages (condensed, visible only on small screens) */}
      <div className="flex items-center gap-1 sm:hidden">
        {mobilePages.map((page, index) => renderPageItem(page, index, true))}
      </div>

      {/* Desktop pages (full, visible on larger screens) */}
      <div className="hidden sm:flex items-center gap-1">
        {desktopPages.map((page, index) => renderPageItem(page, index, false))}
      </div>

      {renderNextButton()}
    </nav>
  );
}
