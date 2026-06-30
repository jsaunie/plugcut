"""Translate domain/application errors into localized HTTP responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.shared.errors import DomainError
from app.interfaces.api.i18n import resolve_locale, translate

# Map error codes to HTTP status; anything unlisted is a 400 Bad Request.
_STATUS_BY_CODE: dict[str, int] = {
    "identity.email_already_registered": 409,
    "identity.invalid_credentials": 401,
    "identity.inactive_user": 403,
    "identity.invalid_token": 401,
    "identity.invalid_email": 422,
    "identity.weak_password": 422,
    "referral.not_found": 404,
    "referral.forbidden": 403,
    "referral.invalid_terms": 422,
    "installment.not_found": 404,
    "installment.already_paid": 409,
    "domain.illegal_state_transition": 409,
    "agreement.not_ready": 409,
    "invitation.not_found": 404,
    "referral.signature_required": 422,
}
_DEFAULT_STATUS = 400


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def _handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        default_locale = request.app.state.settings.default_locale
        locale = resolve_locale(request.headers.get("accept-language"), default_locale)
        return JSONResponse(
            status_code=_STATUS_BY_CODE.get(exc.code, _DEFAULT_STATUS),
            content={"error": {"code": exc.code, "message": translate(exc.code, locale)}},
        )
