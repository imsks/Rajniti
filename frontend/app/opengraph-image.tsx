import { ImageResponse } from "next/og"

export const size = { width: 1200, height: 630 }
export const contentType = "image/png"

export default function Image() {
    return new ImageResponse(
        (
            <div
                style={{
                    fontSize: 48,
                    background: "linear-gradient(135deg, #fff7ed 0%, #ffffff 50%, #f0fdf4 100%)",
                    width: "100%",
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#0F1F3D",
                }}
            >
                <div
                    style={{
                        display: "flex",
                        fontSize: 72,
                        fontWeight: 700,
                        marginBottom: 16,
                    }}
                >
                    Rajniti
                </div>
                <div style={{ display: "flex", fontSize: 32, color: "#64748b" }}>
                    Know Your Elected Representatives
                </div>
            </div>
        ),
        { ...size }
    )
}
