from __future__ import annotations

import re


DEFAULT_SPOKEN_CORRECTIONS = {
    "amazon.com.mx": "Amazon punto com punto eme equis",
    "tiktok shop": "Tik Tok Shop",
    "chatgpt": "Chat ye pe te",
    "api": "a pe i",
    "ia": "i a",
}


def normalize_spoken(text: str, extra: dict[str, str] | None = None) -> str:
    corrections = {**DEFAULT_SPOKEN_CORRECTIONS, **(extra or {})}
    result = text
    for source in sorted(corrections, key=len, reverse=True):
        result = re.sub(re.escape(source), corrections[source], result, flags=re.IGNORECASE)
    return result


def normalize_caption(text: str, extra: dict[str, str] | None = None) -> str:
    result = text.strip()
    for source, target in (extra or {}).items():
        result = re.sub(re.escape(source), target, result, flags=re.IGNORECASE)
    return result
