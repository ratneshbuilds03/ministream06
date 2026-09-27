from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.subscription_service import (
    follow_creator, unfollow_creator,
    get_followers, get_following,
    is_following, get_subscription_stats
)
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.post("/follow/{creator_id}")
async def follow(
    creator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result, error = await follow_creator(db, current_user.id, creator_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result

@router.delete("/unfollow/{creator_id}")
def unfollow(
    creator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result, error = unfollow_creator(db, current_user.id, creator_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result

@router.get("/followers/{user_id}")
def followers(
    user_id: int,
    page: int = 1,
    db: Session = Depends(get_db)
):
    return get_followers(db, user_id, page)

@router.get("/following/{user_id}")
def following(
    user_id: int,
    page: int = 1,
    db: Session = Depends(get_db)
):
    return get_following(db, user_id, page)

@router.get("/check/{creator_id}")
def check_following(
    creator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    following = is_following(db, current_user.id, creator_id)
    return {"is_following": following, "creator_id": creator_id}

@router.get("/stats/{user_id}")
def subscription_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    return get_subscription_stats(db, user_id)

@router.get("/my/following")
def my_following(
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_following(db, current_user.id, page)

@router.get("/my/followers")
def my_followers(
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_followers(db, current_user.id, page)