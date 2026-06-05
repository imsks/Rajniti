// "use client";

// import React from "react";
// import PoliticianCard from "@/components/PoliticianCard";
// import type { Politician } from "@/types/politician";

// interface DashboardPoliticianCardProps {
//   politician: Politician;
//   showRecentlyUpdatedBadge?: boolean;
// }

// /** Check if politician was updated in the last 7 days */
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

// export default function DashboardPoliticianCard({
//   politician,
//   showRecentlyUpdatedBadge = false,
// }: DashboardPoliticianCardProps) {
//   const recentlyUpdated =
//     showRecentlyUpdatedBadge && isRecentlyUpdated(politician.updated_at);

//   return (
//     <div className="relative">
//       {/* Recently Updated Badge - Positioned absolutely at top-left */}
//       {recentlyUpdated && (
//         <div className="absolute -top-3 -left-2 z-10">
//           <span className="inline-flex px-3 py-1 bg-green-500 dark:bg-green-600 rounded-full text-xs font-bold text-white shadow-md">
//             Recently Updated
//           </span>
//         </div>
//       )}

//       {/* Card */}
//       <PoliticianCard politician={politician} />
//     </div>
//   );
// }
