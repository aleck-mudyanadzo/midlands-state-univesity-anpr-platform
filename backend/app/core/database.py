from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


def create_database_engine(database_url: str) -> Engine:
    engine_options = {"pool_pre_ping": True}
    if make_url(database_url).get_backend_name() == "sqlite":
        engine_options["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, **engine_options)


engine = create_database_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()