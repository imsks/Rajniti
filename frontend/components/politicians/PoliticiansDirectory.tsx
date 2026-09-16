import Pagination from "@/components/ui/Pagination";
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
  return (
    <Pagination
      currentPage={page}
      totalPages={totalPages}
      buildHref={(p) => buildPoliticiansPath(p, filters)}
    />
  );
}
