from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.redis_client import cache_delete_pattern
import logging

logger = logging.getLogger(__name__)

async def add_comment(
    mongo_db: AsyncIOMotorDatabase,
    content_id: int,
    user_id: int,
    user_name: str,
    username: str,
    text: str,
    parent_id: str = None
) -> tuple:
    if not text or len(text.strip()) < 1:
        return None, "Comment cannot be empty"

    if len(text) > 1000:
        return None, "Comment too long (max 1000 chars)"


    if parent_id:
        try:
            parent = await mongo_db.comments.find_one(
                {"_id": ObjectId(parent_id)}
            )
            if not parent:
                return None, "Parent comment not found"
            if parent.get("is_deleted"):
                return None, "Cannot reply to deleted comment"
        except Exception:
            return None, "Invalid parent comment ID"

    comment = {
        "content_id": content_id,
        "user_id": user_id,
        "user_name": user_name,
        "username": username,
        "text": text.strip(),
        "parent_id": parent_id,
        "likes": 0,
        "liked_by": [],
        "reply_count": 0,
        "is_deleted": False,
        "is_edited": False,
        "created_at": datetime.utcnow(),
        "updated_at": None
    }

    result = await mongo_db.comments.insert_one(comment)
    comment["id"] = str(result.inserted_id)
    del comment["_id"]
    del comment["liked_by"]

    
    if parent_id:
        await mongo_db.comments.update_one(
            {"_id": ObjectId(parent_id)},
            {"$inc": {"reply_count": 1}}
        )

    
    cache_delete_pattern(f"comments:{content_id}:*")

    return format_comment(comment), None

async def get_comments(
    mongo_db: AsyncIOMotorDatabase,
    content_id: int,
    page: int = 1,
    per_page: int = 20
) -> dict:
    skip = (page - 1) * per_page

    comments = await mongo_db.comments.find(
        {"content_id": content_id, "parent_id": None, "is_deleted": False},
        {"liked_by": 0}
    ).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)

    result = []
    for comment in comments:
        comment_dict = format_comment(comment)


        replies = await mongo_db.comments.find(
            {
                "parent_id": str(comment["_id"]) if "_id" in comment else comment.get("id"),
                "is_deleted": False
            },
            {"liked_by": 0}
        ).sort("created_at", 1).limit(3).to_list(3)

        comment_dict["top_replies"] = [format_comment(r) for r in replies]
        result.append(comment_dict)

    total = await mongo_db.comments.count_documents(
        {"content_id": content_id, "parent_id": None, "is_deleted": False}
    )

    return {
        "comments": result,
        "total": total,
        "page": page,
        "has_more": (skip + per_page) < total
    }

async def get_replies(
    mongo_db: AsyncIOMotorDatabase,
    comment_id: str,
    page: int = 1,
    per_page: int = 20
) -> dict:
    skip = (page - 1) * per_page

    replies = await mongo_db.comments.find(
        {"parent_id": comment_id, "is_deleted": False},
        {"liked_by": 0}
    ).sort("created_at", 1).skip(skip).limit(per_page).to_list(per_page)

    total = await mongo_db.comments.count_documents(
        {"parent_id": comment_id, "is_deleted": False}
    )

    return {
        "replies": [format_comment(r) for r in replies],
        "total": total,
        "page": page
    }
    
async def update_comment(
    mongo_db: AsyncIOMotorDatabase,
    comment_id: str,
    user_id: int,
    new_text: str,
    is_admin: bool = False
) -> tuple:
    try:
        comment = await mongo_db.comments.find_one(
            {"_id": ObjectId(comment_id)}
        )
    except Exception:
        return None, "Invalid comment ID"

    if not comment:
        return None, "Comment not found"

    if not is_admin and comment["user_id"] != user_id:
        return None, "Permission denied"

    if not new_text or len(new_text.strip()) < 1:
        return None, "Comment cannot be empty"

    await mongo_db.comments.update_one(
        {"_id": ObjectId(comment_id)},
        {
            "$set": {
                "text": new_text.strip(),
                "is_edited": True,
                "updated_at": datetime.utcnow()
            }
        }
    )

    updated = await mongo_db.comments.find_one(
        {"_id": ObjectId(comment_id)},
        {"liked_by": 0}
    )
    return format_comment(updated), None


async def delete_comment(
    mongo_db: AsyncIOMotorDatabase,
    comment_id: str,
    user_id: int,
    is_admin: bool = False
) -> tuple:
    try:
        comment = await mongo_db.comments.find_one(
            {"_id": ObjectId(comment_id)}
        )
    except Exception:
        return False, "Invalid comment ID"

    if not comment:
        return False, "Comment not found"

    if not is_admin and comment["user_id"] != user_id:
        return False, "Permission denied"

    await mongo_db.comments.update_one(
        {"_id": ObjectId(comment_id)},
        {
            "$set": {
                "is_deleted": True,
                "text": "[Comment deleted]",
                "updated_at": datetime.utcnow()
            }
        }
    )

    cache_delete_pattern(f"comments:{comment['content_id']}:*")
    return True, None

async def toggle_comment_like(
    mongo_db: AsyncIOMotorDatabase,
    comment_id: str,
    user_id: int
) -> tuple:
    try:
        comment = await mongo_db.comments.find_one(
            {"_id": ObjectId(comment_id)}
        )
    except Exception:
        return None, "Invalid comment ID"

    if not comment:
        return None, "Comment not found"

    liked_by = comment.get("liked_by", [])

    if user_id in liked_by:
        await mongo_db.comments.update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$inc": {"likes": -1},
                "$pull": {"liked_by": user_id}
            }
        )
        action = "unliked"
    else:
        await mongo_db.comments.update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$inc": {"likes": 1},
                "$push": {"liked_by": user_id}
            }
        )
        action = "liked"

    updated = await mongo_db.comments.find_one(
        {"_id": ObjectId(comment_id)},
        {"liked_by": 0}
    )

    return {
        "action": action,
        "likes": updated["likes"],
        "comment_id": comment_id
    }, None


def format_comment(comment: dict) -> dict:
    if not comment:
        return None
    comment = dict(comment)
    if "_id" in comment:
        comment["id"] = str(comment["_id"])
        del comment["_id"]
    if "liked_by" in comment:
        del comment["liked_by"]
    if "created_at" in comment and hasattr(comment["created_at"], "isoformat"):
        comment["created_at"] = comment["created_at"].isoformat()
    if "updated_at" in comment and comment["updated_at"] and hasattr(comment["updated_at"], "isoformat"):
        comment["updated_at"] = comment["updated_at"].isoformat()
    return comment