import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL = re.compile(r"(?:https?://|www\.)\S+|\b(?:linkedin|github)\.com/\S+", re.IGNORECASE)
PHONE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)")


def _phone_sub(match: re.Match) -> str:
    # Only treat it as a phone number if it has enough digits (keeps "2019 - 2023" intact).
    digits = sum(ch.isdigit() for ch in match.group(0))
    return "[phone]" if digits >= 9 else match.group(0)


def redact(text: str) -> str:
    """Removes direct identifiers before text goes to any analysis model."""
    text = EMAIL.sub("[email]", text)
    text = URL.sub("[link]", text)
    text = PHONE.sub(_phone_sub, text)
    return text