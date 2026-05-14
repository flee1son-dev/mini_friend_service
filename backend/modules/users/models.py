from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Date
from backend.core.database import Base
from datetime import date

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    first_name: Mapped[str] = mapped_column(nullable=False)

    last_name: Mapped[str] = mapped_column(nullable=False)

    birth_date: Mapped[date] = mapped_column(Date, nullable=True)

    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)

    password: Mapped[str] = mapped_column(nullable=False)

    is_active: Mapped[bool] = mapped_column(nullable=False)

    sent_friendships: Mapped[list["Friendship"]] = relationship(
        "Friendship",
        foreign_keys="[Friendship.requester_id]",
        back_populates="requester",
        cascade="all, delete-orphan"
    )

    received_friendships: Mapped[list["Friendship"]] = relationship(
        "Friendship",
        foreign_keys="[Friendship.addressee_id]",
        back_populates="addressee",
        cascade="all, delete-orphan"
    )



    

