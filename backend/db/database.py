from sqlmodel import create_engine, Session
from ..config.config_client import ConfigClient

_sql_url = ConfigClient.get_property("sql_url", "DATABASE")
connect_args = {"check_same_thread": False}

engine = create_engine(_sql_url, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session
