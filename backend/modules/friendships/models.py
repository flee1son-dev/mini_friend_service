from sqlalchemy import ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from backend.core.database import Base
from backend.modules.users.models import User
from enum import Enum as PyEnum

class FriendshipStatus(PyEnum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Friendship(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    requester_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    addressee_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    status: Mapped[FriendshipStatus] = mapped_column(
        SQLAEnum(FriendshipStatus, name="friendship_status"),
        default=FriendshipStatus.pending,
        nullable=False
    )

    requester: Mapped["User"] = relationship("User", foreign_keys=[requester_id])
    addressee: Mapped["User"] = relationship("User", foreign_keys=[addressee_id])
    
