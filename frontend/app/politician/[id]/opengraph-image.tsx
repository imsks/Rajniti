import { ImageResponse } from "next/og"
import { fetchPoliticianBySegment } from "@/lib/api/politicians-server"
import { buildPoliticianDescription } from "@/lib/seo/metadata"
import { toTitleCase } from "@/lib/politicianUtils"

export const size = { width: 1200, height: 630 }
export const contentType = "image/png"
export const alt = "Politician profile"
export const runtime = "nodejs"

export default async function Image({
    params,
}: {
    params: Promise<{ id: string }>
}) {
    const { id } = await params
    const politician = await fetchPoliticianBySegment(id)

    if (!politician) {
        return new ImageResponse(
            (
                <div
                    style={{
                        fontSize: 48,
                        background: "#fff7ed",
                        width: "100%",
                        height: "100%",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "#0F1F3D",
                    }}
                >
                    Rajniti — Politician Profile
                </div>
            ),
            { ...size }
        )
    }

    const description = buildPoliticianDescription(politician).slice(0, 120)

    return new ImageResponse(
        (
            <div
                style={{
                    fontSize: 36,
                    background: "linear-gradient(135deg, #fff7ed 0%, #ffffff 100%)",
                    width: "100%",
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    padding: 64,
                    color: "#0F1F3D",
                }}
            >
                <div style={{ display: "flex", fontSize: 24, color: "#ea580c", marginBottom: 12 }}>
                    {politician.type} · {politician.constituency}
                </div>
                <div style={{ display: "flex", fontSize: 56, fontWeight: 700, marginBottom: 24, lineHeight: 1.2 }}>
                    {toTitleCase(politician.name)}
                </div>
                <div style={{ display: "flex", fontSize: 28, color: "#64748b", lineHeight: 1.4 }}>{description}</div>
            </div>
        ),
        { ...size }
    )
}
