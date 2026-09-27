from sqlalchemy import Column, Integer, ForeignKey ,DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base

class Subscription(Base):
    __tablename__ = "subcriptions"
    
    id=Column(Integer, primary_key=True, index=True)
    subscriber_id=Column(Integer, ForeignKey("users.id"),nullable=False)
    creator_id=Column(Integer, ForeignKey("users.id"),nullable=False)
    creator_at=Column(DateTime(timezone=True),server_default=func.now())
    
    __table_args__ =(
        UniqueConstraint(
            "subscriber_id",
            "creator_id",
            name="unique_subscription"
        ),
    )