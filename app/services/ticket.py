from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket
from app.policy import AccessContext, BusinessElement, Permission
from app.repositories import ticket as ticket_repo
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse


def _ticket_permissions(access_context: AccessContext) -> set[Permission]:
    return access_context.permissions.get(BusinessElement.TICKETS.value, set())


def _ensure_owner_or_all(
    ticket: Ticket,
    access_context: AccessContext,
    all_permission: Permission,
) -> None:
    if all_permission in _ticket_permissions(access_context):
        return

    if ticket.owner_id != access_context.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )


async def list_tickets(
    db: AsyncSession,
    access_context: AccessContext,
) -> list[TicketResponse]:
    if Permission.READ_ALL in _ticket_permissions(access_context):
        tickets_obj = await ticket_repo.list_tickets(db)
        tickets = [
            TicketResponse.model_validate(obj)
            for obj in tickets_obj
        ]
        return tickets

    tickets_obj = await ticket_repo.list_tickets_by_owner(db, access_context.user_id)
    tickets = [
        TicketResponse.model_validate(obj)
        for obj in tickets_obj
    ]
    return tickets


async def get_ticket(
    db: AsyncSession,
    ticket_id: int,
    access_context: AccessContext,
) -> Ticket:
    ticket = await ticket_repo.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    _ensure_owner_or_all(ticket, access_context, Permission.READ_ALL)
    return ticket


async def create_ticket(
    db: AsyncSession,
    ticket_create: TicketCreate,
    access_context: AccessContext,
) -> Ticket:
    ticket = Ticket(
        **ticket_create.model_dump(),
        status="open",
        owner_id=access_context.user_id,
        assignee_id=None,
    )
    db.add(ticket)

    try:
        await db.commit()
        await db.refresh(ticket)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during ticket creation",
        ) from exc

    return ticket


async def update_ticket(
    db: AsyncSession,
    ticket_id: int,
    ticket_update: TicketUpdate,
    access_context: AccessContext,
) -> Ticket:
    ticket = await ticket_repo.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    _ensure_owner_or_all(ticket, access_context, Permission.UPDATE_ALL)
    update_data = ticket_update.model_dump(exclude_unset=True)

    if Permission.UPDATE_ALL not in _ticket_permissions(access_context):
        forbidden_fields = {"priority", "assignee_id"}
        if forbidden_fields.intersection(update_data):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )

    for field, value in update_data.items():
        setattr(ticket, field, value)

    try:
        await db.commit()
        await db.refresh(ticket)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during ticket update",
        ) from exc

    return ticket


async def delete_ticket(
    db: AsyncSession,
    ticket_id: int,
    access_context: AccessContext,
) -> None:
    ticket = await ticket_repo.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    _ensure_owner_or_all(ticket, access_context, Permission.DELETE_ALL)
    await db.delete(ticket)

    try:
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during ticket deletion",
        ) from exc
