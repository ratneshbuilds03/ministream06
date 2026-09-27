from fastapi import APIRouter ,Depends,Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.search_services import(
    search_content,search_creators,
    get_content_by_category,get_all_categories
)

router =APIRouter(prefix="/search",tags=["Search"])

@router.get("/content")
async def search_content_endpoint(
    q: str = Query(..., min_length=2),
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "relevance",
    page: int = 1,
    db: Session = Depends(get_db)
):
    return search_content(db, q, content_type, category, sort_by, page)

@router.get("/creators")
async def search_creators_endpoint(
    q: str = Query(..., min_length=2),
    page: int = 1,
    db: Session = Depends(get_db)
):
    return search_creators(db, q, page)

@router.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    return get_all_categories(db)

@router.get("/category/{category}")
async def content_by_category(
    category: str,
    page: int = 1,
    db: Session = Depends(get_db)
):
    return get_content_by_category(db, category, page)