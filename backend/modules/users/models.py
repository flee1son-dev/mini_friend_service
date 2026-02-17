from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Date
from backend.core.database import Base
from datetime import date

class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    first_name: Mapped[str] = mapped_column(nullable=False)

    last_name: Mapped[str] = mapped_column(nullable=False)

    birth_date: Mapped[date] = mapped_column(Date, nullable=True)

    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)

    password: Mapped[str] = mapped_column(nullable=False)

    is_active: Mapped[bool] = mapped_column(nullable=False)



    

