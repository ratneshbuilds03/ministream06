from fastapi import APIRouter ,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.mongodb import get_mongodb
from app.services.analytics_service import(
    get_creator_stats,get_platform_stats,get_content_analytics
)
from app.utils.dependencies import get_current_user,require_creator
from app.models.user import User

router =APIRouter(prefix="/anlytics",tags=["Analytics"])

@router.get("/me")
async def my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_creator)
):
    return get_creator_stats(db, current_user.id)

@router.get("/content/{content_id}")
async def content_analytics(
    content_id: int,
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongodb),
    current_user: User = Depends(require_creator)
):
    result = await get_content_analytics(
        mongo_db, content_id, current_user.id, db
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Content not found or permission denied"
        )
    return result

@router.get("/platform")
async def platform_stats(
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongodb)
):
    return await get_platform_stats(db, mongo_db)