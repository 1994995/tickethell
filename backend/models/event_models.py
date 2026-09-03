from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
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
    from .ticket_models import Ticket

class EventBase(SQLModel):
    name: str = Field(index=True)
    location: str = Field(index=True)
    timestamp: datetime = Field(default=None, index=True)  # `default=None` just for debug/testing so I don't have to deal with it rn

class Event(EventBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: uuid.UUID = Field(default_factory=uuid.uuid4)
    tickets: list["Ticket"] = Relationship(back_populates="event")

class EventPublic(EventBase):
    id: int

class EventCreate(EventBase):
    pass

class EventUpdate(SQLModel):
    name: str | None = None
    location: str | None = None
    timestamp: datetime | None = None