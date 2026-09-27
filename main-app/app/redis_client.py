import redis
import json
from app.config import settings

def get_redis():
    return redis.from_url(settings.REDIS_URL, decode_responses=True)

def cache_set(key: str, data, expire:int=300):
    try:
        get_redis().setex(key,expire,json.dumps(data))
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False
    
def cache_get(key:str):
    try:
        data = get_redis().get(key)
        return json.loads(data) if data else None
    except Exception as e:
        print(f"Cache get error: {e}")
        return None

def cache_delete(key:str):
    try:
        get_redis().delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False

def cache_delete_pattern(pattern:str):
    try:
        client=get_redis()
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
        return True
    except Exception as e:
        print(f"Cache delete pattern error: {e}")
        return False
            