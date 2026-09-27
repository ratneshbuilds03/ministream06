from fastapi import APIRouter ,Depends,HTTPException,status,Request
from slowapi import Limiter
from pydantic import BaseModel , Field
from typing import Optional
from app.mongodb import get_mongodb
from app.services.comment_service import(
    add_comment, get_comments,get_replies,
    update_comment,delete_comment,toggle_comment_like
)
from app.utils.dependencies import get_current_user
from app.models.user import User
from slowapi.util import get_remote_address


router = APIRouter (prefix="/comments",tags=["Comments"])
limiter = Limiter(key_func=get_remote_address)

class CommentCreate(BaseModel):
    text:str=Field(..., min_length=1,max_length=1000)
    parent_id:Optional[str]=None

class CommentUpdate(BaseModel):
    text:str=Field(...,min_length=1,max_length=1000)
    
@router.get("/content/{content_id}")
async def list_comments(
    content_id:int,
    page:int=1,
    mongo_db = Depends(get_mongodb)
):
    return await get_comments(mongo_db,content_id,page)

@router.get("/{comment_id}/replies")
async def list_replies(
    comment_id:str,
    page:int=1,
    mongo_db = Depends(get_mongodb)
):
    return await get_replies(mongo_db,comment_id,page)

@router.post("/content/{content_id}",status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_comment(
    request:Request,
    content_id:int,
    comment_data:CommentCreate,
    mongo_db = Depends(get_mongodb),
    current_user:User=Depends(get_current_user)
):
    comment, error =await add_comment(
        mongo_db=mongo_db,
        content_id=content_id,
        user_id=current_user.id,
        user_name=current_user.name,
        username=current_user.username,
        text=comment_data.text,
        parent_id=comment_data.parent_id
    )
    
    if error:
        raise HTTPException(status_code=400,detail=error)
    return comment

@router.put("/{comment_id}")
async def edit_comment(
    comment_id:str,
    comment_data:CommentUpdate,
    mongo_db=Depends(get_mongodb),
    current_user:User=Depends(get_current_user)
):
    comment, error = await update_comment(
        mongo_db,comment_id,
        current_user.id,comment_data.text
    )
    if error:
        raise HTTPException(status_code=400,detail=error)
    return comment

@router.delete("/{comment_id}",status_code=204)
async def remove_comment(
    comment_id:str,
    mongo_db=Depends(get_mongodb),
    current_user:User=Depends(get_current_user)
):
    success,error = await delete_comment(
        mongo_db,comment_id,current_user.id
    )
    if error:
        raise HTTPException(status_code=400,detail=error)
    
@router.post("/{comment_id}/like")
async def like_comment(
    comment_id:str,
    mongo_db=Depends(get_mongodb),
    current_user:User=Depends(get_current_user)
):
    result,error = await toggle_comment_like(
        mongo_db,comment_id,current_user.id
    )
    if error:
        raise HTTPException(status_code=400,detail=error)
    return result
