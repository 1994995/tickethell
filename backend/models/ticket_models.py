from typing import Optional, TYPE_CHECKING, ClassVar
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
import uuid

from datetime import datetime

'''This prevents circular import error as 
types are not imposed at run time for annotations
and are not enforced at runtime

reference: 
    https://github.com/fastapi/full-stack-fastapi-template/issues/406
    https://stackoverflow.com/questions/79023460/handling-circular-imports-in-pydantic-models-with-fastapi
'''
if TYPE_CHECKING:
    from .event_models import Event

class TicketBase(SQLModel):
    first_name: str | None = Field(index=True)
    last_name: str | None = Field(index=True)
    email: EmailStr | None = Field(index=True)
    
class Ticket(TicketBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: uuid.UUID = Field(default_factory=uuid.uuid4)

    qr_value: str | None = Field(default=None)

    event_id: int = Field(foreign_key="event.id")
    event: Event = Relationship(back_populates="tickets")

    payment_id: int | None = Field(default=None, index=True)
    scanned: datetime | None = Field(default=None)

class TicketPublic(TicketBase):
    id: int

class TicketCreate(TicketBase):
    event_id: int
    number: Optional[int] = 1

class TicketUpdate(SQLModel):
    scanned: datetime | None = None