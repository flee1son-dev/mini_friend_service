from sqlalchemy.orm import sessionmaker, declarative_base
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

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close