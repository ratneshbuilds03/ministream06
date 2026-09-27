from sqlalchemy import Column, Integer, String,  Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class UserRole:
    CREATOR="creator"
    VIEWER="viewer"
    ADMIN="admin"
    ALL=[CREATOR, VIEWER, ADMIN]
    
class User(Base):
    __tablename__ ="users"
    
    id =Column(Integer,primary_key=True,index=True)
    name =Column(String(100),nullable=False)
    username =Column(String(50),unique=True,nullable=False,index=True)
    email =Column(String(120),unique=True,nullable=False,index=True)
    password_hash =Column(String(255),nullable=False)
    role =Column(String(20),default=UserRole.VIEWER)
    bio =Column(Text,nullable=True)
    avatar_role =Column(String(500),nullable=True)
    is_active =Column(Boolean,default=True)
    is_verified =Column(Boolean,default=False)
    follower_count =Column(Integer,default=0)
    following_count =Column(Integer,default=0)
    created_at =Column(DateTime(timezone=True),server_default=func.now())
    
    def to_dict(self):
        return{
            "id":self.id,
            "name":self.name,
            "username":self.username,
            "email":self.email,
            "password_hash":self.password_hash,
            "role":self.role,
            "bio":self.bio,
            "avatar_role":self.avatar_role,
            "is_active":self.is_active,
            "is_verified":self.is_verified,
            "follower_count":self.follower_count,
            "following_count":self.following_count,
            "created_at":self.created_at.isoformat()
        }