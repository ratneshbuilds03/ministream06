from sqlalchemy.orm import Session
from app.models.content import Content,ContentStatus
from app.models.subscription import Subscription
from app.services.redis_service import cache_user_feed,get_cached_feed
import logging

logger = logging.getLogger(__name__)

def get_user_feed(
    db:Session,
    user_id:int,
    page:int=1,
    per_page:int=20
):
    cache_key_with_page= f"{user_id}:{page}"
    cached = get_cached_feed(cache_key_with_page)
    
    if cached:
        logger.info(f"Feed Cache HIT for user {user_id}")
        return cached
    logger.info(f"Feed Cache MISS for user {user_id}")
    
    Subscribed_creator_ids = db.query(
        Subscription.creator_id
    ).filter(
        Subscription.subscriber_id==user_id
    ).all()
    
    creator_ids = [c[0] for c in Subscribed_creator_ids]
    if not creator_ids:
        contents = db.query(Content).filter(
            Content.status == ContentStatus.PUBLISHED
        ).order_by(Content.views_count.desc()).limit(20).all()
    else:
        offset = (page -1)* per_page
        contents = db.query(Content).filter(
            Content.creator_id.in_(creator_ids),
            Content.status ==ContentStatus.PUBLISHED
            
        ).order_by(Content.created_at.desc()).offset(offset).limit(per_page).all()
    
    result = {
        "feed":[c.to_dict() for  c in contents],
        "total": len(contents),
        "page":page,
        "subscribed_creators":len(creator_ids)
    }
    
    cache_user_feed(cache_key_with_page,result,expires=300)
    return result