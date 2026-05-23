import { revalidatePath, revalidateTag } from "next/cache"
import {
    politicianProfilePath,
    politicianRevalidationTag,
} from "@/lib/revalidation/politician"

export interface RevalidatePoliticianResult {
    tag: string
    path: string
}

export function parseRevalidatePoliticianSegment(body: {
    segment?: string
    slug?: string
    id?: string
}): string | null {
    const segment = (body.segment ?? body.slug ?? body.id)?.trim()
    return segment || null
}

export function revalidatePoliticianProfile(segment: string): RevalidatePoliticianResult {
    const tag = politicianRevalidationTag(segment)
    const path = politicianProfilePath(segment)
    revalidateTag(tag, "max")
    revalidatePath(path)
    return { tag, path }
}

export function isAuthorizedRevalidationRequest(
    secret: string | undefined,
    headerSecret: string | null
): boolean {
    return Boolean(secret && headerSecret === secret)
}
