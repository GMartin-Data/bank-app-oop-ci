"""
This file contains all the logic devoted to manage the database.
Note that init_db_connection returns two objects:
- an engine,
- a session
It seems better to return both, even if you'll mainly use
session via context managers.
Indeed, returning the engine will allow to close all connections
afterwards with `engine.dispose()`
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .bank import Base


def init_db_connection(debug=False):
    engine = create_engine("sqlite:///bank.db", echo=debug)
    Base.metadata.create_all(engine)  # This always checks if table already exists beforehand
    return engine, sessionmaker(bind=engine)