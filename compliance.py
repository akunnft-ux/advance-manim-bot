import re


DISALLOWED_PATTERNS = [
    r"comment.*if you",
    r"comment.*if agree",
    r"tag.*friends",
    r"tag \d+",
    r"share this.*to see",
    r"share.*to win",
    r"like if you",
    r"follow if you",
]


def compliance_check(caption: str):
    caption_lower = caption.lower()
    for pattern in DISALLOWED_PATTERNS:
        if re.search(pattern, caption_lower):
            raise ValueError(f"Compliance: engagement bait pattern '{pattern}' detected")
    return True
