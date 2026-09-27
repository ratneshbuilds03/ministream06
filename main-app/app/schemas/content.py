from pydantic import BaseModel , Field
from typing import Optional , List
from datetime import datetime

class ContentCreate(BaseModel):
    title: str = Field(...,min_length=3, max_length=300)
    description:Optional[str]=Field(None,max_length=2000)
    content_type:str = Field(...,pattern="^(video|image|article)$")
    category:Optional[str]=None
    tags:Optional[List[str]]=[]
    
class ContentUpdate(BaseModel):
    title:Optional[str]=Field(None,min_length=3,max_length=300)
    description:Optional[str]=None
    status:Optional[str]=Field(None,pattern="^(draft|published|archived)$")
    category:Optional[str]=None
    tags:Optional[List[str]]=None
    

class ContentResponse(BaseModel):
    id:int
    title:str
    description:Optional[str]
    content_type:str
    status:str
    file_url:Optional[str]
    thumbnail_url:Optional[str]
    duration:Optional[float]
    category:Optional[str]
    tags:List[str]
    views_count:int
    likes_count:int
    comments_count:int
    creator_id:int
    created_at:datetime
    
    class Config:
        from_attributes=True

class ContentListResponse(BaseModel):
    contents:List[ContentResponse]
    total:int
    page:int
    pages:int
    
    
