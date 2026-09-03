from typing import Union
from pydantic import EmailStr
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from ..db.database import get_session

from ..models.ticket_models import Ticket, TicketPublic, TicketCreate, TicketUpdate
from ..core.qr_code import encode_uuid_utf, generate_qr_buffer
from ..core.email import send_ticket_email

from datetime import datetime

router = APIRouter(
    prefix="/ticket",
    tags=["Ticket"]
)

@router.post("/add_ticket", response_model=Union[TicketPublic, list[TicketPublic]])
def add_ticket(ticket: TicketCreate, session: Session=Depends(get_session)):
    """Add ticket(s) to the database with an `event_id` foreign_key associating
    them with an event

    `TicketCreate` defines a field `number` which allows the creation of multiple tickets
    from a single API call (most likely after the payment has been effectuated)

    TODO: raise error if event_id does not exist already?

    Args:
        ticket (TicketCreate): Required fields for creating a new ticket
        session (Session, optional): DB Session. Defaults to Depends(get_session).

    Returns:
        TicketPublic | list[TicketPublic]: _description_
    """
    if ticket.number > 1:
        '''The only reason this block of code exists is because,
        for some reason, `SQLModel` refuses to call pydantic
        `@field_validator` when `table=True` meaning you can't
        run a computation post validation to set the model field
        based on the value of another field
        '''
        ticket_list: list[Ticket] = []
        for _ in range(ticket.number):
            t = Ticket.model_validate(ticket.model_dump(exclude_unset=True,
                                                        exclude_computed_fields=True))  # Excludes `id` and `uuid` (at the very least)
            t.qr_value = encode_uuid_utf(t.uuid.bytes)
            ticket_list.append(t)

        '''`add_all` technically just iterates each element and calls `add`
        this isn't that big of a deal for us rn, but might be worth thinking about
        using a more optimized `insert` query'''
        session.add_all(ticket_list)
        session.commit()  # This refreshes the session (for some reason)
        return ticket_list

    db_ticket = Ticket.model_validate(ticket)
    db_ticket.qr_value = encode_uuid_utf(db_ticket.uuid.bytes)

    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)
    return db_ticket

'''I'm thinking something like this being invoked as a callback from the frontend
once it receives confirmation from `add_ticket`
Presumably (if everything goes well) there will be some update to some content or whatever
which can invoke this at the same time and (if there is a problem) will prevent
potentially triggering this function 
but idk'''
@router.get("/send_ticket")
def send_ticket(event_id: int, email: EmailStr, background_tasks: BackgroundTasks,
                session: Session=Depends(get_session)):
    """Send QR codes for ticket to `email` through SMTP

    Right now the exact functionality by which this would be called is somewhat ambiguous.
    I am envisioning something like (payment flow) -> Add Ticket -> return add confirmation
    -> frontend does something and makes a callback -> confirm email send

    Args:
        event_id (int): _description_
        email (EmailStr): _description_
        background_tasks (BackgroundTasks): _description_
        session (Session, optional): _description_. Defaults to Depends(get_session).

    Returns:
        _type_: _description_
    """
    statement = select(Ticket).where(Ticket.event_id == event_id,
                                     Ticket.email == email)
    '''`all` as there may be multiple tickets associated to the individual
    `generate_qr_buffer` will handle dealing with the number of tickets
    for code generation'''
    ticket_list = session.exec(statement).all()  # TODO: check if there is no match found and return requisite error code

    qr_buffer = generate_qr_buffer(ticket_list)
    # Don't love having these hardcoded but whatever for this kind of project
    ext = "pdf" if len(ticket_list) > 1 else "png"

    file_name = ticket_list[0].event.name
    background_tasks.add_task(send_ticket_email, email, qr_buffer,
                              file_name, ext)

    # TODO: Proper messages on return
    return 200

@router.put("/scan_ticket", response_model=TicketPublic)
def scan_ticket(qr_scan: str, session: Session=Depends(get_session)):
    """Checks whether the value received from scanned QR code matches
    a value in the database and marks that ticket as `scanned`

    Args:
        qr_scan (str): value scanned/received from qr code scan (or perhaps some manual attendance button)
        session (Session, optional): DB Session. Defaults to Depends(get_session).

    Raises:
        HTTPException: 404 - No match for `qr_value` in DB
        HTTPException: 409 - There are multiple identical values which match `qr_scan`
        HTTPException: 423 - Ticket has already been scanned and another scan was requested

    Returns:
        TicketPublic: Updated values of `Ticket` from DB
    """
    statement = select(Ticket).where(Ticket.qr_value == qr_scan)
    db_ticket = session.exec(statement).all()  # Using `all` because `one` returns a server error if not found
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if db_ticket[0].scanned is not None:
        raise HTTPException(status_code=423, detail="Ticket already scanned!")
    if len(db_ticket) > 1:
        # ? Not sure if `409` is really the best code to use here tbh
        raise HTTPException(status_code=409, detail="Multiple tickets for qr value")

    ticket = db_ticket[0]  # This feels kind of wonky to do tbh, but prefer it to having it in the middle of except handling
    ticket.sqlmodel_update({"scanned": datetime.now()})

    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket
