from fastapi import APIRouter, Depends , HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, Token, UserUpdate
from app.services.auth_service import signup_user, login_user
from app.utils.dependencies import get_current_user, get_optional_current_user
from app.models.user import User
from app.services.redis_service import create_session,delete_session
from app.services.subscription_service import get_subscription_stats,is_following
from typing import Optional


router = APIRouter (prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(user:UserCreate, db:Session= Depends(get_db)):
    new_user, error = signup_user(db, user)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return new_user

@router.post("/login",response_model=Token)
def login(
    from_data:OAuth2PasswordRequestForm = Depends(),
    db:Session=Depends(get_db)
):
    result, error = login_user(db, from_data.username, from_data.password)
    if error:
        raise HTTPException(status_code=401, detail=error)
    create_session(
        user_id=result["user"]["id"],
        token=result["access_token"],
        expires=3600
    )
    return result

@router.get("/me",response_model=UserResponse)
def get_me(current_user:User= Depends(get_current_user)):
    return current_user

@router.put("/me",response_model=UserResponse)
def update_profile(
    data:UserUpdate,
    current_user: User = Depends(get_current_user),
    db:Session= Depends(get_db)
):
    if data.name:
        current_user.name=data.name
    if data.bio is not None:
        current_user.bio = data.bio
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/users/{username}",response_model=UserResponse)
def get_user_profile(username:str,db:Session=Depends(get_db),current_user:Optional[User]=Depends(get_optional_current_user)):
    user = db.query(User).filter(User.username==username.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = user.to_dict()
    
    stats = get_subscription_stats(db,user.id)
    profile["followers"] = stats["followers"]
    profile["following"] = stats["following"]
    
    if current_user:
        profile["is_following"]= is_following(
            db,current_user.id,user.id
        )
    return profile

@router.post("/logout")
def logout(current_user:User=Depends(get_current_user)):
    delete_session(current_user.id)
    return {"message":"Logged out successfully"}

