"""Minimal i18n for API error messages, keyed by stable domain error codes.

Domain/application errors carry a ``code``; the API never exposes raw English. The
front-end has its own full i18n catalog — this one localizes server-side responses
(errors, emails) so the API is usable directly in FR or EN.
"""

from __future__ import annotations

SUPPORTED_LOCALES = ("fr", "en")
FALLBACK_LOCALE = "en"

MESSAGES: dict[str, dict[str, str]] = {
    "identity.email_already_registered": {
        "fr": "Cet email est déjà utilisé.",
        "en": "This email is already registered.",
    },
    "identity.invalid_credentials": {
        "fr": "Identifiants invalides.",
        "en": "Invalid credentials.",
    },
    "identity.inactive_user": {
        "fr": "Ce compte est désactivé.",
        "en": "This account is inactive.",
    },
    "identity.invalid_token": {
        "fr": "Jeton d'authentification invalide ou expiré.",
        "en": "Invalid or expired authentication token.",
    },
    "identity.invalid_email": {
        "fr": "Adresse email invalide.",
        "en": "Invalid email address.",
    },
    "identity.weak_password": {
        "fr": "Mot de passe trop court (8 caractères minimum).",
        "en": "Password is too short (8 characters minimum).",
    },
    "referral.not_found": {
        "fr": "Ce deal est introuvable.",
        "en": "This deal was not found.",
    },
    "referral.forbidden": {
        "fr": "Tu n'as pas accès à ce deal.",
        "en": "You do not have access to this deal.",
    },
    "referral.invalid_terms": {
        "fr": "Les conditions de commission sont invalides.",
        "en": "The commission terms are invalid.",
    },
    "installment.not_found": {
        "fr": "Cette échéance est introuvable.",
        "en": "This installment was not found.",
    },
    "installment.already_paid": {
        "fr": "Cette échéance est déjà réglée.",
        "en": "This installment is already paid.",
    },
    "domain.illegal_state_transition": {
        "fr": "Cette action n'est pas possible à ce stade du deal.",
        "en": "This action is not allowed at this stage of the deal.",
    },
    "agreement.not_ready": {
        "fr": "Le contrat sera disponible une fois le deal signé.",
        "en": "The agreement is available once the deal is signed.",
    },
    "invitation.not_found": {
        "fr": "Cette invitation est invalide ou expirée.",
        "en": "This invitation is invalid or expired.",
    },
    "referral.signature_required": {
        "fr": "La signature est requise.",
        "en": "A signature is required.",
    },
    "contact.not_found": {
        "fr": "Ce contact est introuvable.",
        "en": "This contact was not found.",
    },
    "contact.forbidden": {
        "fr": "Tu n'as pas accès à ce contact.",
        "en": "You do not have access to this contact.",
    },
    "contact.name_required": {
        "fr": "Le nom du contact est requis.",
        "en": "The contact name is required.",
    },
    "domain.error": {
        "fr": "Une erreur est survenue.",
        "en": "An error occurred.",
    },
}


def translate(code: str, locale: str) -> str:
    entry = MESSAGES.get(code, MESSAGES["domain.error"])
    return entry.get(locale, entry[FALLBACK_LOCALE])


def resolve_locale(accept_language: str | None, default: str) -> str:
    """Pick a supported locale from an Accept-Language header, else the default."""
    if accept_language:
        for part in accept_language.split(","):
            tag = part.split(";")[0].strip().lower()[:2]
            if tag in SUPPORTED_LOCALES:
                return tag
    return default if default in SUPPORTED_LOCALES else FALLBACK_LOCALE
