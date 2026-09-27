from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.subscription import Subscription
from app.models.user import User
from app.services.redis_service import (
    invalidate_feed, cache_set, cache_get,
)
from app.services.notification_client import notify_new_follower
import logging

logger = logging.getLogger(__name__)

async def follow_creator(
    db: Session,
    subscriber_id: int,
    creator_id: int
):
    
    if subscriber_id == creator_id:
        return None, "Cannot follow yourself"


    creator = db.query(User).filter(User.id == creator_id).first()
    if not creator:
        return None, "Creator not found"


    existing = db.query(Subscription).filter(
        Subscription.subscriber_id == subscriber_id,
        Subscription.creator_id == creator_id
    ).first()

    if existing:
        return None, "Already following this creator"

    try:

        subscription = Subscription(
            subscriber_id=subscriber_id,
            creator_id=creator_id
        )
        db.add(subscription)

    
        creator.follower_count += 1

        subscriber = db.query(User).filter(User.id == subscriber_id).first()
        subscriber.following_count += 1

        db.commit()

    
        invalidate_feed(str(subscriber_id))

        
        await notify_new_follower(
            follower_name=subscriber.name,
            creator_email=creator.email
        )

        return {
            "message": f"Now following {creator.name}",
            "creator": creator.to_dict()
        }, None

    except IntegrityError:
        db.rollback()
        return None, "Already following this creator"
    except Exception as e:
        db.rollback()
        logger.error(f"Follow error: {e}")
        return None, "Failed to follow"

def unfollow_creator(
    db: Session,
    subscriber_id: int,
    creator_id: int
):
    subscription = db.query(Subscription).filter(
        Subscription.subscriber_id == subscriber_id,
        Subscription.creator_id == creator_id
    ).first()

    if not subscription:
        return None, "Not following this creator"


    db.delete(subscription)

    creator = db.query(User).filter(User.id == creator_id).first()
    if creator and creator.follower_count > 0:
        creator.follower_count -= 1

    subscriber = db.query(User).filter(User.id == subscriber_id).first()
    if subscriber and subscriber.following_count > 0:
        subscriber.following_count -= 1

    db.commit()

    invalidate_feed(str(subscriber_id))

    return {"message": f"Unfollowed successfully"}, None

def get_followers(
    db: Session,
    creator_id: int,
    page: int = 1,
    per_page: int = 20
):
    cache_key = f"followers:{creator_id}:{page}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    offset = (page - 1) * per_page

    followers = db.query(User).join(
        Subscription,
        Subscription.subscriber_id == User.id
    ).filter(
        Subscription.creator_id == creator_id
    ).offset(offset).limit(per_page).all()

    total = db.query(Subscription).filter(
        Subscription.creator_id == creator_id
    ).count()

    result = {
        "followers": [u.to_dict() for u in followers],
        "total": total,
        "page": page
    }

    cache_set(cache_key, result, expire=120)
    return result

def get_following(
    db: Session,
    user_id: int,
    page: int = 1,
    per_page: int = 20
):
    cache_key = f"following:{user_id}:{page}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    offset = (page - 1) * per_page

    following = db.query(User).join(
        Subscription,
        Subscription.creator_id == User.id
    ).filter(
        Subscription.subscriber_id == user_id
    ).offset(offset).limit(per_page).all()

    total = db.query(Subscription).filter(
        Subscription.subscriber_id == user_id
    ).count()

    result = {
        "following": [u.to_dict() for u in following],
        "total": total,
        "page": page
    }

    cache_set(cache_key, result, expire=120)
    return result

def is_following(
    db: Session,
    subscriber_id: int,
    creator_id: int
) -> bool:
    return db.query(Subscription).filter(
        Subscription.subscriber_id == subscriber_id,
        Subscription.creator_id == creator_id
    ).first() is not None

def get_subscription_stats(
    db: Session,
    user_id: int
) -> dict:
    followers_count = db.query(Subscription).filter(
        Subscription.creator_id == user_id
    ).count()

    following_count = db.query(Subscription).filter(
        Subscription.subscriber_id == user_id
    ).count()

    return {
        "followers": followers_count,
        "following": following_count
    }