from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from typing import Generator
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/textprocessor")

engine = create_engine(DATABASE_URL)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

def init_db(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)