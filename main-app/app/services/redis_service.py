import json 
from datetime import datetime
from app.redis_client import get_redis,cache_set,cache_get
import logging

logger = logging.getLogger(__name__)

def track_view(content_id:int,user_id:int=None):
    try:
        client=get_redis()
        client.zincrby("trending:views",1,str(content_id))
        client.pfadd(f"content:{content_id}:unique_views",str(user_id or "anonymous"))
        hour_key=f"views:hourly:{datetime.utcnow().strftime('%Y%m%d%H')}"
        client.zincrby(hour_key,1,str(content_id))
        client.expire(hour_key,86400)
        return True
    except Exception as e:
        logger.error(f"View tracking error: {e}")
        return False

def get_view_count(content_id:int)-> int:
    try:
        client = get_redis()
        score = client.zscore("trending:views",str(content_id))
        return int(score) if score else 0
    except Exception as e:
        logger.error(f"Get view count error:{e}")
        return 0
    
def get_unique_views(content_id:int) -> int:
    try:
        client = get_redis()
        return client.pfcount(f"content:{content_id}:unique_views")
    except Exception as e:
        logger.error(f"Get unique views error: {e}")
        return 0
    
def get_trending_content(limit:int=10) -> list:
    try:
        client = get_redis()
        trending = client.zrevrange(
            "trending:views",0,limit-1,withscores=True
        )
        return[
            {"content_id":int(cid),"views":int(score)}
            for cid, score in trending
        ]
        
    except Exception as e:
        logger.error(f"Trending error:{e}")
        return []
def get_trending_by_category(category: str, limit: int = 10) -> list:
    try:
        client = get_redis()
        trending = client.zrevrange(
            f"trending:{category}", 0, limit - 1, withscores=True
        )
        return [
            {"content_id": int(cid), "views": int(score)}
            for cid, score in trending
        ]
    except Exception as e:
        logger.error(f"Category trending error: {e}")
        return []

    
def track_category_view(content_id,category:str):
    try:
        client = get_redis()
        if category:
            client.zincrby(f"trending:{category}",1,str(content_id))
    except Exception as e:
        logger.error(f"Category view tracking error: {e}")
        
def toggle_like(content_id:int,user_id:int) -> dict:
    try:
        client = get_redis()
        like_key = f"content:{content_id}:likes"
        
        if client.sismember(like_key,str(user_id)):
            client.srem(like_key,str(user_id))
            action = "unliked"
        else:
            client.sadd(like_key,str(user_id))
            action = "liked"
        likes_count =client.scard(like_key)
        return {"action":action,"likes_count":likes_count}
    except Exception as e:
        logger.error(f"Toggle like error:{e}")
        return{"action":"error","likes_count":0}
    
def get_likes_count(content_id:int) -> int:
    try:
        return get_redis().scard(f"content:{content_id}:likes")
    except Exception as e:
        logger.error(f"Get likes error: {e}")
        return 0
    
def has_user_liked(content_id:int, user_id:int) ->bool:
    try:
        return bool(get_redis().sismember(
            f"content:{content_id}:likes",str(user_id)
        ))
    except Exception as e:
        logger.error(f"Check like error: {e}")
        return False
def create_session(user_id:int, token:str,expires:int=3600):
    try:
        client = get_redis()
        session_data ={
            "user_id":user_id,
            "created_at":datetime.utcnow().isoformat(),
            "token":token[:20]+"..."
        }
        client.setex(
            f"session:{user_id}",
            expires,
            json.dumps(session_data)
        )
        return True
    except Exception as e:
        logger.error(f"Session create error: {e}")
        return False

def get_session(user_id:int)-> dict:
    try:
        data=get_redis().get(f"session:{user_id}")
        return json.loads(data) if data else None
    except Exception as e:
        logger.error(f"Get session error: {e}")
        return None
    
def  delete_session(user_id:int):
    try:
        get_redis().delete(f"session:{user_id}")
        return True
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        return False
    
def refresh_session(user_id:int,expires:int =3600):
    try:
        get_redis().expire(f"session:{user_id}",expires)
        return True
    except Exception as e:
        logger.error(f"Refresh session error: {e}")
        return False
    
def check_rate_limit(
    key:str,
    limit:int,
    window:int=60
) -> dict:
    try:
        client = get_redis()
        current = client.get(key)
        
        if current is None:
            client.setex(key,window,1)
            return {"allowed":True, "remaining":limit-1}
        current = int(current)
        if current >= limit:
            ttl = client.ttl(key)
            return {
                "allowed":False,
                "remaining":0,
                "retry_after":ttl
            }
            
        client.incr(key)
        return {"allowed":True, "remaining":limit-current-1}
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return {"allowed":True,"remaining":limit}
    
def cache_user_feed(user_id:int,feed_data:list,expires: int =300):
    try:
        get_redis().setex(
            f"feed:{user_id}",
            expires,
            json.dumps(feed_data)
        )
        return True
    except Exception as e:
        logger.error(f"Feet cache error: {e}")
        return False

def get_cached_feed(user_id:int)->list:
    try:
        data=get_redis().get(f"feed:{user_id}")
        return json.loads(data) if data else None
    except Exception as e:
        logger.error(f"Get feed cache error: {e}")
        return None
def invalidate_feed(user_id:int):
    try:
        get_redis().delete(f"feed:{user_id}")
        return True
    except Exception as e:
        logger.error(f"Invalidate feed error: {e}")
        return False

