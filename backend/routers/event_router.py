from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException
from ..models.event_models import Event, EventPublic, EventCreate, EventUpdate
from ..models.ticket_models import Ticket, TicketPublic

from ..db.database import get_session

router = APIRouter(
    prefix="/event",
    tags=["Event"]
)

@router.post("/add_event", response_model=EventPublic)
def add_event(event: EventCreate, session: Session=Depends(get_session)):
    """Add a new event to the database

    Args:
        event (EventCreate): Model fields required for adding event to database
        session (Session, optional): DB Session. Defaults to Depends(get_session).

    Returns:
        EventPublic: updated public fields added to DB
    """
    db_event = Event.model_validate(event)
    session.add(db_event)
    session.commit()
    session.refresh(db_event)

    return db_event

@router.get("/event_tickets", response_model=list[TicketPublic])
def get_event_tickets(event_id: int, session: Session=Depends(get_session)):
    """Get all tickets associated with the event

    Args:
        event_id (int): primary_key of event 
        session (Session, optional): DB Session. Defaults to Depends(get_session).

    Returns:
        list[TicketPublic]: list of every ticket with foreign_key to event
    """
    # TODO: `NotFound` handling
    statement = select(Event).where(Event.id == event_id)
    result = session.exec(statement).one()

    return result.tickets

@router.patch("/event_update/{event_id}", response_model=EventPublic)
def update_event(event_id: int, event: EventUpdate, 
                 session: Session=Depends(get_session)):
    """Update data related to the event

    Args:
        event_id (int): primary_key of event
        event (EventUpdate): body with values to be updated
        session (Session, optional): DB Session. Defaults to Depends(get_session).

    Raises:
        HTTPException: 404 - `event_id` does not exist in DB

    Returns:
        EventPublic: `EventPublic` with updated data for event
    """
    db_event = session.get(Event, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    event_data = event.model_dump(exclude_unset=True)
    db_event.sqlmodel_update(event_data)

    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event
