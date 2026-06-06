# pyrefly: ignore [missing-import]
from sqlmodel import SQLModel, create_engine, Session as DBSession
from app.config import settings

# Create engine. If it's sqlite, we need special connect_args
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)

def init_db():
    # Create database tables if they do not exist
    SQLModel.metadata.create_all(engine)

def get_db_session():
    with DBSession(engine) as session:
        yield session
