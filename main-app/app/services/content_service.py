from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.content import Content,ContentStatus
from app.models.user import User
from app.schemas.content import ContentCreate, ContentUpdate
from app. redis_client import cache_set,cache_get,cache_delete_pattern,cache_delete
import logging

logger = logging.getLogger(__name__)

def create_content(
    db:Session,
    content_data:ContentCreate,
    creator_id: int,
    file_url: str=None,
    thumbnail_url:str=None,
    file_size:int=None

):
    new_content=Content(
        title=content_data.title,
        description=content_data.description,
        content_type=content_data.content_type,
        category=content_data.category,
        tags=",".join(content_data.tags)if content_data.tags else None,
        file_url=file_url,
        thumbnail_url=thumbnail_url,
        file_size=file_size,
        creator_id=creator_id,
        status=ContentStatus.DRAFT
    )
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    
    cache_delete_pattern(f"content:list:*")
    cache_delete_pattern(f"content:creator:{creator_id}:*")
    
    return new_content

def get_all_content(
    db:Session,
    page:int=1,
    per_page:int=12,
    content_type:str=None,
    category:str=None,
    status:str=ContentStatus.PUBLISHED
):
    cache_key = f"content:list{status}:{content_type}:{category}:{page}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    query =db.query(Content).filter(Content.status==status)
    
    if content_type:
        query = query.filter(Content.content_type==content_type)
    if category:
        query = query.filter(Content.category==category)
        
    total = query.count()
    offset = (page - 1) * per_page
    contents = query.order_by(
        Content.created_at.desc()
    ).offset(offset).limit(per_page).all()

    pages = (total + per_page - 1) // per_page 
    result = {
        "contents":[c.to_dict() for c in contents],
        "total":total,
        "page":page,
        "pages":pages
    }
    
    cache_set(cache_key, result,expire=120)
    return result
def get_content_by_id(db:Session,contnet_id:int):
    cache_key=f"content:{contnet_id}"
    cached=cache_get(cache_key)
    if cached:
        return cached
    content = db.query(Content).filter(Content.id==contnet_id).first()
    if not content:
        return None
    result = content.to_dict()
    cache_set(cache_key,result,expire=300)
    return result

def get_creator_content(
    db: Session,
    creator_id: int,
    page: int = 1,
    per_page: int = 12
):
    cache_key = f"content:creator:{creator_id}:{page}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    query = db.query(Content).filter(Content.creator_id == creator_id)
    total = query.count()
    offset = (page - 1) * per_page
    contents = query.order_by(
        Content.created_at.desc()
    ).offset(offset).limit(per_page).all()
    
    result = {
        "contents": [c.to_dict() for c in contents],
        "total": total,
        "page": page,
        "pages": (total+per_page -1 )//per_page
    }

    cache_set(cache_key, result, expire=120)
    return result



def update_content(
    db:Session,
    content_id:int,
    content_date:ContentUpdate,
    current_user_id:int
):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        return None, "Content not found"
    if content.creator_id != current_user_id:
        return None, "Permission denied"
    if content_date.title:
        content.title=content_date.title
    if content_date.description is not None:
        content.description =content_date.description
    if content_date.status:
        content.status=content_date.status
    if content_date.category:
        content.category= content_date.category
    if content_date.tags is not None:
        content.tags = ",".join(content_date.tags)
        
    db.commit()
    db.refresh(content)

    cache_delete_pattern(f"content:{content_id}")
    cache_delete_pattern("content:list:*")
    
    return content.to_dict(), None

def delete_content(db:Session, content_id:int,current_user_id:int):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        return False, "Content not found"
    
    if content.creator_id != current_user_id:
        return False, "Permission denied"
    
    if content.file_url:
        from app.services.s3_service import deleted_from_s3
        deleted_from_s3(content.file_url)
    if content.thumbnail_url:
        from app.services.s3_service import deleted_from_s3
        deleted_from_s3(content.thumbnail_url)
        
    db.delete(content)
    db.commit()
    
    cache_delete_pattern(f"content:{content_id}")
    cache_delete_pattern("content:list:*")
    cache_delete_pattern(f"content:creator:{current_user_id}:*")
    
    return True, None

def increment_view_count(db:Session, content_id:int):
    content =db.query(Content).filter(Content.id == content_id).first()
    if content:
        content.views_count +=1
        db.commit()
        cache_delete_pattern(f"content:{content_id}")
    