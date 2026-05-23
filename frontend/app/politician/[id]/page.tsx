import { Suspense } from "react";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import PoliticianPageClient from "./PoliticianPageClient";
import JsonLd from "@/components/seo/JsonLd";
import {
  fetchPoliticianBySegment,
  PoliticianApiUnreachableError,
} from "@/lib/api/politicians-server";
import {
  buildPersonJsonLd,
  buildPoliticianBreadcrumbJsonLd,
} from "@/lib/seo/json-ld";
import { buildPoliticianMetadata } from "@/lib/seo/metadata";
import { getPreferredPoliticianPath } from "@/lib/seo/politician-canonical";
/** ISR — revalidate politician profiles periodically; on-demand via /api/revalidate/politician. */
export const revalidate = 3600;

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  let politician = null;
  try {
    politician = await fetchPoliticianBySegment(id);
  } catch (e) {
    if (e instanceof PoliticianApiUnreachableError) {
      return { title: "Profile temporarily unavailable" };
    }
    throw e;
  }
  if (!politician) {
    return {
      title: "Politician not found",
      robots: { index: false, follow: false },
    };
  }

  return buildPoliticianMetadata(politician);
}

export default async function PoliticianPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const politician = await fetchPoliticianBySegment(id);
  if (!politician) notFound();

  const canonicalPath = getPreferredPoliticianPath(politician);

  return (
    <>
      <JsonLd
        data={[
          buildPersonJsonLd(politician, canonicalPath),
          buildPoliticianBreadcrumbJsonLd(politician),
        ]}
      />
      <Suspense
        fallback={
          <div className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 flex items-center justify-center">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent" />
              <p className="mt-4 text-gray-600 dark:text-gray-400 font-semibold">
                Loading…
              </p>
            </div>
          </div>
        }
      >
        <PoliticianPageClient politician={politician} routeSegment={id} />
      </Suspense>
    </>
  );
}
