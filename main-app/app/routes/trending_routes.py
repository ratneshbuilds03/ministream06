from fastapi import APIRouter , Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.redis_service import(
    get_trending_content , get_trending_by_category
)
from app.models.content import Content
from app.redis_client import cache_get,cache_set

router = APIRouter(prefix="/trending",tags=["Trending"])

@router.get("/")
async def trending(
    limit:int =10,
    db:Session=Depends(get_db)
):
    cache_key= f"trending:global:{limit}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    trending_ids = get_trending_content(limit)
    
    contents = []
    for item in trending_ids:
        content_obj = db.query(Content).filter(
            Content.id ==item["content_id"]
        ).first()
        if content_obj:
            content_dict=content_obj.to_dict()
            content_dict["trending_views"]= item["views"]
            contents.append(content_dict)
            
    result = {"trending": contents, "total":len(contents)}
    
    cache_set(cache_key,result,expire=120)
    return result

@router.get("/category/{category}")
async def trending_by_category(
    category:str,
    limit:int=10,
    db:Session=Depends(get_db)
):
    trending_ids= get_trending_by_category(category,limit)
    
    contents =[]
    for item in trending_ids:
        content_obj =db.query(Content).filter(
            Content.id ==item["content_id"]
        ).first()
        if content_obj:
            content_dict=content_obj.to_dict()
            content_dict["trending_views"]=item["views"]
            contents.append(content_dict)
            
    return{
        "category":category,
        "trending":contents,
        "total":len(contents)
    
}