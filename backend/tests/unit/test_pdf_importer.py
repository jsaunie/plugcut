"""Unit tests for the heuristic profile-text parser used by the PDF importer."""

from __future__ import annotations

from app.infrastructure.contacts.pdf_importer import parse_profile_text


class TestParseProfileText:
    def test_extracts_name_headline_and_linkedin(self) -> None:
        text = (
            "Marie Martin\n"
            "Coach indépendante\n"
            "Paris, France\n"
            "www.linkedin.com/in/mariemartin\n"
            "Expérience: 10 ans de coaching."
        )
        data = parse_profile_text(text)
        assert data.full_name == "Marie Martin"
        assert data.headline == "Coach indépendante"
        assert data.linkedin_url == "https://www.linkedin.com/in/mariemartin"
        assert "Expérience" in data.notes

    def test_empty_text_yields_empty_suggestion(self) -> None:
        data = parse_profile_text("")
        assert data.full_name == ""
        assert data.headline == ""
        assert data.linkedin_url is None
