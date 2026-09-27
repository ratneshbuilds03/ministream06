from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.content import Content,ContentStatus
from app.models.subscription import Subscription
from app.services.redis_service import get_trending_content,get_view_count
from datetime import datetime , timedelta
import logging

logger = logging.getLogger(__name__)

def get_creator_stats(db: Session, creator_id: int) -> dict:
    
    total_content = db.query(Content).filter(
        Content.creator_id == creator_id
    ).count()

    published = db.query(Content).filter(
        Content.creator_id == creator_id,
        Content.status == ContentStatus.PUBLISHED
    ).count()

    
    total_views = db.query(
        func.sum(Content.views_count)
    ).filter(
        Content.creator_id == creator_id
    ).scalar() or 0

    
    total_likes = db.query(
        func.sum(Content.likes_count)
    ).filter(
        Content.creator_id == creator_id
    ).scalar() or 0

    total_followers = db.query(Subscription).filter(
        Subscription.creator_id == creator_id
    ).count()

    top_content = db.query(Content).filter(
        Content.creator_id == creator_id,
        Content.status == ContentStatus.PUBLISHED
    ).order_by(Content.views_count.desc()).limit(5).all()

    content_by_type = {}
    type_results = db.query(
        Content.content_type,
        func.count(Content.id)
    ).filter(
        Content.creator_id == creator_id
    ).group_by(Content.content_type).all()

    for content_type, count in type_results:
        content_by_type[content_type] = count

    return {
        "total_content": total_content,
        "published_content": published,
        "draft_content": total_content - published,
        "total_views": int(total_views),
        "total_likes": int(total_likes),
        "total_followers": total_followers,
        "content_by_type": content_by_type,
        "top_content": [c.to_dict() for c in top_content]
    }

async def get_platform_stats(
    db: Session,
    mongo_db: AsyncIOMotorDatabase
) -> dict:
    total_users = db.query(Content).count()
    total_content = db.query(Content).filter(
        Content.status == ContentStatus.PUBLISHED
    ).count()

    total_views = db.query(
        func.sum(Content.views_count)
    ).scalar() or 0

    total_subscriptions = db.query(Subscription).count()

    total_comments = await mongo_db.comments.count_documents(
        {"is_deleted": False}
    )


    trending = get_trending_content(5)

    return {
        "total_content": total_content,
        "total_views": int(total_views),
        "total_subscriptions": total_subscriptions,
        "total_comments": total_comments,
        "trending_now": trending
    }
    
async def get_content_analytics(
    mongo_db: AsyncIOMotorDatabase,
    content_id: int,
    creator_id: int,
    db: Session
) -> dict:
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.creator_id == creator_id
    ).first()

    if not content:
        return None

    redis_views = get_view_count(content_id)

    total_comments = await mongo_db.comments.count_documents(
        {"content_id": content_id, "is_deleted": False}
    )

    top_comments = await mongo_db.comments.find(
        {"content_id": content_id, "is_deleted": False}
    ).sort("likes", -1).limit(3).to_list(3)

    for c in top_comments:
        c["id"] = str(c["_id"])
        del c["_id"]
        if "liked_by" in c:
            del c["liked_by"]

    return {
        "content_id": content_id,
        "title": content.title,
        "mysql_views": content.views_count,
        "redis_views": redis_views,
        "likes": content.likes_count,
        "total_comments": total_comments,
        "top_comments": top_comments,
        "created_at": content.created_at.isoformat()
    }
