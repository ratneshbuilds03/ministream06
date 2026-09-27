from app.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

client = None
db = None

async def connect_mongodb():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    print("MongoDB Connected")
    
async def close_mongodb():
    global client
    if client:
        client.close()
        
def get_mongodb():
    return db