from pydantic import BaseModel ,EmailStr ,Field
from typing import Optional

class UserCreate(BaseModel):
    name:str=Field(...,min_length=2,max_length=100)
    username:str = Field(...,min_length=3,max_length=50,pattern="^[a-zA-Z0-9_]+$")
    email:EmailStr
    password:str=Field(...,min_length=7,max_length=72)
    role:str="viewer"
        
class UserLogin(BaseModel):
    email:EmailStr
    password:str=Field(...,min_length=6,max_length=72)
    
class UserResponse(BaseModel):
    id:int
    name:str
    username:str
    email:str
    role:str
    bio:Optional[str]=None
    avatar_url:Optional[str]=None
    is_verified:bool
    follower_count:int
    following_count:int
        
    class config:
        from_attributes = True
        
class UserUpdate(BaseModel):
    name:Optional[str]=Field(None,min_length=2,max_length=100)
    bio:Optional[str]=Field(None,max_length=500)
class Token(BaseModel):
    access_token:str
    token_type:str="bearer"
    user:UserResponse