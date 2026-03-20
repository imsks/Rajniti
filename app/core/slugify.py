import unicodedata


def slugify(value: str) -> str:
    """
    Create an SEO-friendly slug:
    - lowercase
    - hyphen-separated
    - remove special characters
    """
    if value is None:
        return ""

    s = unicodedata.normalize("NFKD", str(value))

    out: list[str] = []
    prev_sep = False
    for ch in s:
        if ch.isalnum():
            out.append(ch.lower())
            prev_sep = False
        else:
            if not prev_sep:
                out.append("-")
                prev_sep = True

    slug = "".join(out).strip("-")
    # Defensive: collapse multiple hyphens (should already be minimal).
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug


def short_id_from_uuid(uuid_or_id: str, *, short_len: int = 8) -> str:
    """
    For our dataset we use UUID v4-like strings.
    We extract the first segment before '-' (e.g. "8fba2f3f-b5...").
    """
    if not uuid_or_id:
        return ""

    u = uuid_or_id.strip().lower()
    first = u.split("-", 1)[0]
    if len(first) >= short_len:
        return first[:short_len]
    # Fallback when input isn't hyphenated.
    return u[:short_len]

