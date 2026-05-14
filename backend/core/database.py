from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine
from backend.core.config import settings

engine = create_engine(
    url= settings.DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=True,
    autocommit=False
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close