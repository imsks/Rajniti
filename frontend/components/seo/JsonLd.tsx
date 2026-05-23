export default function JsonLd({ data }: { data: Record<string, unknown> | Record<string, unknown>[] }) {
    const payload = Array.isArray(data) ? data : [data]
    return (
        <>
            {payload.map((record, index) => (
                <script
                    key={index}
                    type="application/ld+json"
                    dangerouslySetInnerHTML={{ __html: JSON.stringify(record) }}
                />
            ))}
        </>
    )
}
