"""Enumerations for the contacts bounded context."""

from __future__ import annotations

from enum import StrEnum


class ContactKind(StrEnum):
    """A contact can be an individual or an organization."""

    PERSON = "person"
    COMPANY = "company"


class ContactSource(StrEnum):
    """How the contact was added."""

    MANUAL = "manual"
    LINKEDIN_PDF = "linkedin_pdf"
    CV = "cv"
