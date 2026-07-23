from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket


async def list_tickets(db: AsyncSession) -> list[Ticket]:
    result = await db.execute(select(Ticket).order_by(Ticket.id))
    return list(result.scalars().all())


async def list_tickets_by_owner(db: AsyncSession, owner_id: int) -> list[Ticket]:
    result = await db.execute(
        select(Ticket)
        .where(Ticket.owner_id == owner_id)
        .order_by(Ticket.id)
    )
    return list(result.scalars().all())


async def get_ticket(db: AsyncSession, ticket_id: int) -> Ticket | None:
    return await db.get(Ticket, ticket_id)
