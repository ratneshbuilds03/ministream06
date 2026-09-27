from sqlalchemy import Column , Integer , String , Boolean , DateTime, Text, Float, ForeignKey , Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ContentType(str, enum.Enum):
    VIDEO="video"
    IMAGE="image"
    ARTICLE="article"

class ContentStatus(str,enum.Enum):
    DRAFT="draft"
    PUBLISHED="published"
    ARCHIVED="archived"
    
class Content(Base):
    __tablename__ = "contents"
    
    id = Column(Integer,primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    content_type =Column(String(20),nullable= False)
    status =Column(String(20),default=ContentStatus.DRAFT)
    file_url =Column(String(500),nullable=True)
    thumbnail_url =Column(String(500),nullable=True)
    duration =Column(Float, nullable=True)
    file_size =Column(Integer,nullable=True)
    category =Column(String(100),nullable=True)
    tags =Column(String(500),nullable=True)
    views_count =Column(Integer,default=0)
    likes_count =Column(Integer,default=0)
    comments_count =Column(Integer,default=0)
    creator_id =Column(Integer,ForeignKey("users.id"),nullable=False)
    created_at =Column(DateTime(timezone=True),server_default=func.now())
    updated_at =Column(DateTime(timezone=True),onupdate=func.now())

    creator = relationship("User",backref="contents")
    
    def to_dict(self):
        return{
            "id":self.id,
            "title":self.title,
            "description":self.description,
            "content_type":self.content_type,
            "status":self.status,
            "file_url":self.file_url,
            "thumbnail_url":self.thumbnail_url,
            "duration":self.duration,
            "file_size":self.file_size,
            "category":self.category,
            "tags":self.tags.split(",") if self.tags else [],
            "views_count":self.views_count,
            "likes_count":self.likes_count,
            "comments_count":self.comments_count,
            "creator_id":self.creator_id,
            "created_at":self.created_at.isoformat(),
            "updated_at":self.updated_at.isoformat() if self.updated_at else None
                
                
        }    
    