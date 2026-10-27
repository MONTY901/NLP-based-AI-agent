
import re


def extract_medicine(text):
    patterns = [
        r"(?:need|find|buy|get|looking for)\s+(.+?)\s+"
        r"(?:medicine|medication|tablets?|capsules?)\b",
        r"(?:medicine|medication|drug)\s+(?:called|named)\s+"
        r"([a-zA-Z0-9 -]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip(" .,!?")

    return None


def understand_request(text):
    query = text.lower()

    distance_match = re.search(
        r"\b(?:within|under|less than|no more than)\s+"
        r"(\d+(?:\.\d+)?)\s*km\b",
        query
    )

    max_km = (
        float(distance_match.group(1))
        if distance_match else None
    )

    wheelchair = any(term in query for term in [
        "wheelchair", "wheel chair", "accessible",
        "step-free", "step free", "no stairs"
    ])

    open_now = any(term in query for term in [
        "open now", "open right now", "currently open"
    ])

    return {
        "wheelchair": wheelchair,
        "open_now": open_now,
        "nearby": any(term in query for term in [
            "near me", "nearby", "nearest", "closest"
        ]),
        "medicine": extract_medicine(text),
        "max_km": max_km
    }
