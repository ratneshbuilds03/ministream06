from sqlalchemy.orm import Session
from sqlalchemy import or_,and_,func
from app.models.content import Content,ContentStatus
from app.models.user import User
from app.redis_client import cache_get ,cache_set
import logging

logger = logging.getLogger(__name__)

def search_content(
    db: Session,
    query: str,
    content_type: str = None,
    category: str = None,
    sort_by: str = "relevance",
    page: int = 1,
    per_page: int = 12
) -> dict:
    if not query or len(query.strip()) < 2:
        return {"results": [], "total": 0, "query": query}

    query = query.strip()
    cache_key = f"search:content:{query}:{content_type}:{category}:{sort_by}:{page}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    search_filter = or_(
        Content.title.ilike(f"%{query}%"),
        Content.description.ilike(f"%{query}%"),
        Content.tags.ilike(f"%{query}%"),
        Content.category.ilike(f"%{query}%")
    )

    db_query = db.query(Content).filter(
        and_(
            Content.status == ContentStatus.PUBLISHED,
            search_filter
        )
    )

    if content_type:
        db_query = db_query.filter(Content.content_type == content_type)
    if category:
        db_query = db_query.filter(Content.category == category)
    if sort_by == "views":
        db_query = db_query.order_by(Content.views_count.desc())
    elif sort_by == "likes":
        db_query = db_query.order_by(Content.likes_count.desc())
    elif sort_by == "latest":
        db_query = db_query.order_by(Content.created_at.desc())
    else:
        
        db_query = db_query.order_by(
            Content.title.ilike(f"%{query}%").desc(),
            Content.views_count.desc()
        )

    total = db_query.count()
    offset = (page - 1) * per_page
    results = db_query.offset(offset).limit(per_page).all()

    result = {
        "results": [c.to_dict() for c in results],
        "total": total,
        "query": query,
        "page": page,
        "pages": (total + per_page - 1) // per_page
    }

    cache_set(cache_key, result, expire=120)
    return result

def search_creators(
    db: Session,
    query: str,
    page: int = 1,
    per_page: int = 12
) -> dict:
    if not query or len(query.strip()) < 2:
        return {"creators": [], "total": 0}

    query = query.strip()

    search_filter = or_(
        User.name.ilike(f"%{query}%"),
        User.username.ilike(f"%{query}%"),
        User.bio.ilike(f"%{query}%")
    )

    db_query = db.query(User).filter(
        and_(
            User.is_active == True,
            search_filter
        )
    ).order_by(User.follower_count.desc())

    total = db_query.count()
    offset = (page - 1) * per_page
    creators = db_query.offset(offset).limit(per_page).all()

    return {
        "creators": [c.to_dict() for c in creators],
        "total": total,
        "query": query,
        "page": page
    }

def get_content_by_category(
    db: Session,
    category: str,
    page: int = 1,
    per_page: int = 12
) -> dict:
    cache_key = f"category:{category}:{page}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    db_query = db.query(Content).filter(
        Content.status == ContentStatus.PUBLISHED,
        Content.category == category
    ).order_by(Content.views_count.desc())

    total = db_query.count()
    offset = (page - 1) * per_page
    contents = db_query.offset(offset).limit(per_page).all()

    result = {
        "contents": [c.to_dict() for c in contents],
        "total": total,
        "category": category,
        "page": page
    }

    cache_set(cache_key, result, expire=300)
    return result
    
def get_all_categories(db: Session) -> list:
    cache_key = "categories:all"
    cached = cache_get(cache_key)
    if cached:
        return cached

    categories = db.query(
        Content.category,
        func.count(Content.id).label("count")
    ).filter(
        Content.status == ContentStatus.PUBLISHED,
        Content.category.isnot(None)
    ).group_by(Content.category).order_by(
        func.count(Content.id).desc()
    ).all()

    result = [
        {"category": cat, "count": count}
        for cat, count in categories
    ]

    cache_set(cache_key, result, expire=600)
    return result