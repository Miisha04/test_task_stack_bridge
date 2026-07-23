from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.policy import AccessContext, BusinessElement, Permission, require_permissions
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.services import ticket as ticket_service


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get(
    "", 
    response_model=list[TicketResponse],
    status_code=status.HTTP_200_OK
)
async def get_tickets(
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.TICKETS, {Permission.READ})
    ),
    db: AsyncSession = Depends(get_db),
) -> list[TicketResponse]:
    return await ticket_service.list_tickets(db, access_context)


@router.get(
    "/{ticket_id}", 
    response_model=TicketResponse, 
    status_code=status.HTTP_200_OK
)
async def get_ticket(
    ticket_id: int,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.TICKETS, {Permission.READ})
    ),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    return await ticket_service.get_ticket(db, ticket_id, access_context)


@router.post(
    "", 
    response_model=TicketResponse, 
    status_code=status.HTTP_201_CREATED
)
async def create_ticket(
    ticket_create: TicketCreate,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.TICKETS, {Permission.CREATE})
    ),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    return await ticket_service.create_ticket(db, ticket_create, access_context)


@router.patch(
    "/{ticket_id}", 
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK
)
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.TICKETS, {Permission.UPDATE})
    ),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    return await ticket_service.update_ticket(db, ticket_id, ticket_update, access_context)


@router.delete(
    "/{ticket_id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_ticket(
    ticket_id: int,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.TICKETS, {Permission.DELETE})
    ),
    db: AsyncSession = Depends(get_db),
) -> None:
    return await ticket_service.delete_ticket(db, ticket_id, access_context)
