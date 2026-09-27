import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL:str=os.getenv("DATABASE_URL")
    MONGODB_URL:str=os.getenv("MONGODB_URL")
    MONGODB_DB:str=os.getenv("MONGODB_DB","ministream_db")
    REDIS_URL:str=os.getenv("REDIS_URL","redis://localhost:6379")
    SECRET_KEY:str=os.getenv("SECRET_KEY")
    ALGORITHM:str=os.getenv("ALGORITHM","HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES:int=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",60))
    AWS_ACCESS_KEY_ID:str=os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY:str=os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME:str=os.getenv("AWS_BUCKET_NAME")
    AWS_REGION:str=os.getenv("AWS_REGION","ap-south-1")
    NOTIFICATION_SERVICE_URL:str=os.getenv("NOTIFICATION_SERVICE_URL","http://localhost:5001")
    
settings = Settings()