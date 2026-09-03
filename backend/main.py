from fastapi import FastAPI
from fastapi_mail import FastMail
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from sqlmodel import SQLModel
'''Importing the table models here (prior to engine + session creation)
ensures '''
from .db.database import engine

from .routers import event_router, ticket_router

import logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("APP")

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(event_router.router)
app.include_router(ticket_router.router)

'''To be updated once we have a better idea as to what
kinds of requests can/should be made, who can make them, etc...
'''
app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_origins=['*'],
    allow_credentials=True,
    allow_headers=["*"]
)