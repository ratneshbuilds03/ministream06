from fastapi import APIRouter , Depends, HTTPException, UploadFile,File,Form,status,BackgroundTasks,logger
from sqlalchemy.orm import Session
from typing import Optional , List
from app.database import get_db
from app.schemas.content import ContentCreate,ContentUpdate,ContentResponse,ContentListResponse
from app.services.content_service import(
    create_content,get_all_content ,
    update_content,delete_content,
    increment_view_count,get_content_by_id,
    get_creator_content)
from app.services.s3_service import(
    validate_content_file, upload_content_to_s3,
    upload_thumbnail_to_s3, generate_presigned_url
)
from app.utils.dependencies import get_current_user, get_optional_current_user, require_creator
from app.models.user import User
from app.redis_client import cache_set , cache_get
from app.services import redis_service
from app.services.feed_service import get_user_feed

router = APIRouter(prefix="/content",tags=["Content"])

@router.post("/upload",status_code=status.HTTP_201_CREATED)
async def upload_content(
    title:str=Form(...,min_length=3),
    description:str=Form(None),
    content_type:str=Form(...),
    category:str = Form(None),
    tags:str = Form(""),
    file:UploadFile=File(...),
    thumbnail :UploadFile = File(None),
    db:Session =Depends(get_db),
    current_user: User = Depends(require_creator)
):
    
    file_content = await file.read()
    validate_content_file(file_content,file.filename,content_type)
    
    file_url = upload_content_to_s3(
        file_content=file_content,
        filename=file.filename,
        content_type=content_type,
        creator_id=current_user.id
    )
    thumbnail_url=None
    if thumbnail:
        thumb_content = await thumbnail.read()
        thumbnail_url = upload_thumbnail_to_s3(thumb_content,current_user.id)
        
    tags_list = [t.strip() for t in tags.split(",") if t.split()] if tags else []
    
    from app.schemas.content import ContentCreate
    content_data = ContentCreate(
        title=title,
        description=description,
        content_type=content_type,
        category=category,
        tags=tags_list
    )
    content = create_content(
        db=db,
        content_data=content_data,
        creator_id=current_user.id,
        file_url=file_url,
        thumbnail_url=thumbnail_url,
        file_size=len(file_content)
    )
    
    return content.to_dict()

@router.get("/",response_model=ContentListResponse)
async def list_content(
    page:int = 1,
    per_page:int =12,
    content_type:Optional[str]=None,
    category:Optional[str]=None,
    db:Session=Depends(get_db)
):
    
    return get_all_content(db,page,per_page,content_type,category)

@router.get("/my",response_model=ContentListResponse)
async def my_content(
    page: int =1,
    db:Session=Depends(get_db),
    current_user:User=Depends(require_creator)
    ):
    return get_creator_content(db,current_user.id,page)

@router.get("/creator/{creator_id}")
async def creator_content(
    creator_id:int,
    page:int=1,
    db:Session=Depends(get_db)
):
    return get_creator_content(db,creator_id,page)

@router.get("/{content_id}")
async def get_content(
    content_id:int,
    db:Session=Depends(get_db),
    current_user:Optional[User]=Depends(get_optional_current_user)
):
    content = get_content_by_id(db,content_id)
    if not content:
        raise HTTPException(status_code=404,detail="Content not found")
    
    user_id = current_user.id if current_user else None
    redis_service.track_view(content_id,user_id)
    
    if content.get("category"):
        redis_service.track_category_view(content_id,content["category"])
        
    content["redis_views"]=redis_service.get_view_count(content_id)
    content["unique_views"]=redis_service.get_unique_views(content_id)
    content["likes_count"]=redis_service.get_likes_count(content_id)
    
    if current_user:
        content["user_has_liked"]=redis_service.has_user_liked(content_id,current_user.id)
    
    if content.get("file_url"):
        content["stream_url"]=generate_presigned_url(
            content["file_url"],expires=7200
        )
    return content

@router.put("/{content_id}")
async def edit_content(
    content_id:int,
    content_data:ContentUpdate,
    db:Session=Depends(get_db),
    current_user:User=Depends(require_creator)
):
    content , error = update_content(db,content_id,content_data,current_user.id)
    if error:
        raise HTTPException(status_code=400,detail=error)
    return content

@router.delete("/{content_id}",status_code=204)
async def remove_content(
    content_id:int,
    db:Session=Depends(get_db),
    current_user:User=Depends(require_creator)
):
    success, error = delete_content(db,content_id,current_user.id)
    if error:
        raise HTTPException(status_code=400,detail=error)


@router.post("/{content_id}/publish")
async def publish_content(
    content_id:int,
    background_tasks:BackgroundTasks,
    db:Session=Depends(get_db),
    current_user:User=Depends(require_creator)
):
    from app.schemas.content import ContentUpdate
    content, error = update_content(
        db, content_id,
        ContentUpdate(status="published"),
        current_user.id
    )
    if error:
        raise HTTPException(status_code=400,detail=error)
    
    from app.services.notification_client import notify_new_content
    from app.models.subscription import Subscription
    from app.models.user import User as UserModel
    
    subscribers = db.query(UserModel).join(
        Subscription,Subscription.subscriber_id==UserModel.id
    ).filter(Subscription.creator_id==current_user.id).all()
    
    
    subscriber_emails = [s.email for s in subscribers]
    subscriber_count = len(subscriber_emails)
    if subscriber_emails:
        background_tasks.add_task(
            notify_new_content_sync,
            creator_name=current_user.name,
            content_title=content["title"],
            subscribers=subscriber_emails
        )
    
    
    return {"message":"Content published","content":content,"notified_subscribers":subscriber_count}
def notify_new_content_sync(
    creator_name:str,
    content_title:str,
    subscribers:list
):
    import asyncio
    import httpx
    from app.config import settings
    try:
        response = httpx.post(
            f"{settings.NOTIFICATION_SERVICE_URL}/notify/new-content",
            json={
                "creator_name":creator_name,
                "content_title":content_title,
                "subscribers":subscribers
            },
            timeout=10.0
        )
        logger.info(f"Notified {len(subscribers)} subscribers")
    except Exception as e:
        logger.error(f"Notification failed: {e}")
@router.post("/{content_id}/like")
async def like_content(
    content_id:int,
    current_user:User=Depends(get_current_user)
):
    result = redis_service.toggle_like(content_id, current_user.id)
    return result

@router.get("/feed/me")
async def my_feed(
    page:int=1,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    return get_user_feed(db,current_user.id,page)

