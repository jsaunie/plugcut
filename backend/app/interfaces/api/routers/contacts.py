"""Contact routes: a private, owner-scoped network address book (CRUD)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.contacts.dtos import ContactData
from app.application.contacts.ports import ContactImporter
from app.application.contacts.use_cases import (
    CreateContact,
    DeleteContact,
    GetContact,
    ListContacts,
    UpdateContact,
)
from app.domain.contacts.enums import ContactSource
from app.interfaces.api.contact_schemas import (
    ContactResponse,
    ContactSuggestionResponse,
    ContactWriteRequest,
)
from app.interfaces.api.deps import (
    CurrentUser,
    get_contact_importer,
    get_create_contact,
    get_delete_contact,
    get_get_contact,
    get_list_contacts,
    get_session,
    get_update_contact,
)

router = APIRouter(prefix="/contacts", tags=["contacts"])


def _to_data(payload: ContactWriteRequest) -> ContactData:
    return ContactData(
        full_name=payload.full_name,
        kind=payload.kind,
        headline=payload.headline,
        email=payload.email,
        phone=payload.phone,
        linkedin_url=payload.linkedin_url,
        company=payload.company,
        location=payload.location,
        tags=tuple(payload.tags),
        notes=payload.notes,
    )


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    payload: ContactWriteRequest,
    current_user: CurrentUser,
    use_case: Annotated[CreateContact, Depends(get_create_contact)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ContactResponse:
    contact = await use_case.execute(current_user.id, _to_data(payload))
    await session.commit()
    return ContactResponse.from_domain(contact)


@router.post("/import", response_model=ContactSuggestionResponse)
async def import_contact(
    current_user: CurrentUser,
    importer: Annotated[ContactImporter, Depends(get_contact_importer)],
    file: Annotated[UploadFile, File()],
    source: Annotated[ContactSource, Query()] = ContactSource.LINKEDIN_PDF,
) -> ContactSuggestionResponse:
    data = await file.read()
    suggestion = importer.suggest(data)
    return ContactSuggestionResponse.from_data(suggestion, source)


@router.get("", response_model=list[ContactResponse])
async def list_contacts(
    current_user: CurrentUser,
    use_case: Annotated[ListContacts, Depends(get_list_contacts)],
) -> list[ContactResponse]:
    contacts = await use_case.execute(current_user.id)
    return [ContactResponse.from_domain(contact) for contact in contacts]


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetContact, Depends(get_get_contact)],
) -> ContactResponse:
    contact = await use_case.execute(contact_id, requester_id=current_user.id)
    return ContactResponse.from_domain(contact)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    payload: ContactWriteRequest,
    current_user: CurrentUser,
    use_case: Annotated[UpdateContact, Depends(get_update_contact)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ContactResponse:
    contact = await use_case.execute(
        contact_id, requester_id=current_user.id, data=_to_data(payload)
    )
    await session.commit()
    return ContactResponse.from_domain(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[DeleteContact, Depends(get_delete_contact)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    await use_case.execute(contact_id, requester_id=current_user.id)
    await session.commit()
