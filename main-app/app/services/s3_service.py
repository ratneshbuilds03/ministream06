import boto3
import uuid
from botocore.exceptions import ClientError
from fastapi import HTTPException
from app.config import settings
import logging

logger = logging.getLogger(__name__)

ALLOWED_VIDEO={"mp4","mov","avi","mkv","webm"}
ALLOWED_IMAGE={"jpg","jpeg","png","gif","webp"}
MAX_VIDEO_SIZE=100*1024*1024
MAX_IMAGE_SIZE=10*1024*1024

def get_s3():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
def get_file_extention(filename:str) -> str:
    return filename.rsplit(".",1)[-1].lower() if "." in filename else ""

def validate_content_file(
    content:bytes,
    filename:str,
    content_type:str
) -> str:
    ext = get_file_extention(filename)
    
    if content_type == "video":
        if ext not in ALLOWED_VIDEO:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid video format. Allowed: {ALLOWED_VIDEO}"
            )
        if len(content) > MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Video too large. Max 100MB"
            )
    elif content_type =="image":
        if ext not in ALLOWED_IMAGE:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image format. Allowed: {ALLOWED_IMAGE}"
            )
        if len(content) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Image too large. Max 10MB"
            )
    return ext

def upload_content_to_s3(
    file_content:bytes,
    filename:str,
    content_type:str,
    creator_id:int,
    folder:str="content") -> str:
    
    try:
        s3 = get_s3()
        bucket=settings.AWS_BUCKET_NAME
        ext= get_file_extention(filename)
        
        type_folder=f"{content_type}s"
        key=f"{folder}/{type_folder}/{creator_id}/{uuid.uuid4()}.{ext}"
        
        mime_types ={
            "mp4":"video/mp4","mov":"video/quicktime",
            "jpg":"image/jpeg","jpeg":"image/jpeg",
            "png":"image/png","gif":"image/gif",
            "webp":"image/webp"
        }
        mime = mime_types.get(ext,"application/octet-stream")
        
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_content,
            ContentType=mime
        )
        
        url = f"https://{bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        logger.info(f"Uploaded to S3: {url}")
        return url
    except ClientError as e:
        logger.error(f"S3 upload error:{e}")
        return None
    
def upload_thumbnail_to_s3(
    file_content:bytes,
    creator_id: int
) -> str:
    try:
        s3 = get_s3()
        bucket = settings.AWS_BUCKET_NAME
        key = f"thumbnails/{creator_id}/{uuid.uuid4()}.jpg"
        
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_content,
            ContentType="image/jpeg"
        )
        return f"https://{bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"

    except Exception as e:
        logger.error(f"Thumbnail upload error: {e}")
        return None
    
def generate_presigned_url(file_url:str, expires:int = 3600) -> str:
    try:
        s3 = get_s3()
        bucket = settings.AWS_BUCKET_NAME
        key = file_url.split(f".amazonaws.com/")[1]
        
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket":bucket,"Key":key},
            ExpiresIn=expires
        )
    except Exception as e:
        logger.error (f"Presigned URL error: {e}")
        return file_url
    
def delete_from_s3(file_url:str) -> bool:
    try:
        s3 =get_s3()
        bucket =settings.AWS_BUCKET_NAME
        key=file_url.split(f".amazonaws.com/")[1]
        s3.delete_object(Bucket=bucket, Key=key)
        return True
    except Exception as e:
        logger.error(f"S3 delete error: {e}")
        return False