"""Best-effort contact extraction from a PDF (LinkedIn profile export or CV).

The parse is heuristic and assistive: it pre-fills a suggestion that the user reviews
and edits before saving. The text-parsing step is a pure function so it is unit-tested
without needing a real PDF.
"""

from __future__ import annotations

import io
import re

from app.application.contacts.dtos import ContactData

_LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[^\s|]+", re.IGNORECASE)
_MAX_NOTES = 4000


def parse_profile_text(text: str) -> ContactData:
    """Turn raw extracted text into a suggested contact (heuristic)."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    full_name = lines[0] if lines else ""
    headline = lines[1] if len(lines) > 1 else ""

    match = _LINKEDIN_RE.search(text)
    linkedin: str | None = None
    if match:
        linkedin = match.group(0)
        if not linkedin.lower().startswith("http"):
            linkedin = f"https://{linkedin}"

    return ContactData(
        full_name=full_name,
        headline=headline,
        linkedin_url=linkedin,
        notes=text.strip()[:_MAX_NOTES],
    )


class PdfContactImporter:
    def suggest(self, data: bytes) -> ContactData:
        return parse_profile_text(self._extract_text(data))

    @staticmethod
    def _extract_text(data: bytes) -> str:
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(data))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception:
            # Unreadable / non-PDF upload: return nothing so the user fills it in.
            return ""
