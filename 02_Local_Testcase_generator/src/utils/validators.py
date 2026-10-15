"""Validators for Jira IDs and other inputs."""

import re
from typing import Optional


def extract_jira_id(text: str) -> Optional[str]:
    """Extract and validate Jira ID from text.

    Looks for patterns like ABC-123, vwo-49, etc.
    Returns the ID in uppercase (e.g., VWO-49) or None if not found.
    """
    # Pattern: at least one letter, followed by alphanumerics, hyphen, then digits
    pattern = r"\b([A-Za-z][A-Za-z0-9]*-\d+)\b"
    match = re.search(pattern, text)
    if match:
        return match.group(1).upper()
    return None


def is_valid_jira_id(jira_id: str) -> bool:
    """Check if the string is a valid Jira ID format.

    Valid format: uppercase letters/numbers, hyphen, digits.
    Example: VWO-49, ABC-123.
    """
    pattern = r"^[A-Z][A-Z0-9]*-\d+$"
    return bool(re.match(pattern, jira_id))


def normalize_url(url: str) -> str:
    """Normalize a URL: strip trailing slash and ensure https (unless localhost)."""
    url = url.rstrip("/")
    if "localhost" not in url and "127.0.0.1" not in url and not url.startswith("https"):
        url = url.replace("http://", "https://")
    return url
