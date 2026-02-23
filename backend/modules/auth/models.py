from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base
from sqlalchemy import DateTime, String
from datetime import datetime

class TokenBlackList(Base):
    __tablename__ = "Token_blacklist"
    
    id: Mapped[int] = mapped_column(primary_key=True)

    jti: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

