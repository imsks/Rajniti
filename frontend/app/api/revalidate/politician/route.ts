import { NextRequest, NextResponse } from "next/server"
import {
    isAuthorizedRevalidationRequest,
    parseRevalidatePoliticianSegment,
    revalidatePoliticianProfile,
} from "@/lib/revalidation/revalidate-politician"

export async function POST(request: NextRequest) {
    const secret = process.env.REVALIDATION_SECRET
    if (!secret) {
        return NextResponse.json(
            { error: "Revalidation not configured" },
            { status: 503 }
        )
    }

    const authHeader = request.headers.get("x-revalidation-secret")
    if (!isAuthorizedRevalidationRequest(secret, authHeader)) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    let body: { segment?: string; slug?: string; id?: string }
    try {
        body = await request.json()
    } catch {
        return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 })
    }

    const segment = parseRevalidatePoliticianSegment(body)
    if (!segment) {
        return NextResponse.json(
            { error: "segment, slug, or id required" },
            { status: 400 }
        )
    }

    const { tag, path } = revalidatePoliticianProfile(segment)
    return NextResponse.json({ revalidated: true, tag, path })
}
