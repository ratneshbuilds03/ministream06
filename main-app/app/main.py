from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base,settings
from app.mongodb import connect_mongodb ,close_mongodb
from app.routes.auth_routes import router as auth_router
import logging
from app.routes.content_routes import router as content_routes
from app.routes.trending_routes import router as trending_routes
from app.routes.subscription_routes import router as subscription_routes
from app.routes.comment_routes import router as comment_router
from app.routes.analytics_routes import router as anlytics_router
from app.routes.search_routes import router as search_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter=Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    await connect_mongodb()
    
    from app.mongodb import get_mongodb
    mongo =get_mongodb()
    if mongo is not None:
        await mongo.comments.create_index([("content_id",1)])
        await mongo.comments.create_index([("parent_id",1)])
        await mongo.comments.create_index([("user_id",1)])
        await mongo.comments.create_index([("created_at",-1)])
        await mongo.comments.create_index(
            [("content_id",1),("parent_id",1),("is_deleted",1)])
        print("MongoDB indexes created")
    from app.models.user import User
    from app.models.content import Content
    from app.models.subscription import Subscription
    Base.metadata.create_all(bind=engine)
    logger.info("MiniStream API started")
    yield
    await close_mongodb()
    logger.info("MiniStream API stopped")
    
app = FastAPI(
    title="MiniStream API",
    description="Scalable content streaming platform",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["Authorization","Content-Type"]
)

app.include_router(auth_router)
app.include_router(content_routes)
app.include_router(trending_routes)
app.include_router(subscription_routes)
app.include_router(comment_router)
app.include_router(search_router)
app.include_router(anlytics_router)
app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)
@app.get("/health")
async def health():
    from app.mongodb import get_mongodb
    from app.redis_client import get_redis
    import httpx

    health_data = {
        "status": "ok",
        "service": "ministream-main-api",
        "version": "1.0.0",
        "services": {
            "mongodb": "unknown",
            "redis": "unknown",
            "notification": "unknown"
        }
    }
    try:
        mongo = get_mongodb()
        if mongo is not None:
            await mongo.command("ping")
            health_data["services"]["mongodb"] = "connected"
        else:
            health_data["services"]["mongodb"] = "not initialized"
    except Exception:
        health_data["services"]["mongodb"] = "disconnected"
        health_data["status"] = "degraded"
    
    try:
        redis = get_redis()
        redis.ping()
        health_data["services"]["redis"] = "connected"
    except Exception:
        health_data["services"]["redis"] = "disconnected"
        health_data["status"] = "degraded"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.NOTIFICATION_SERVICE_URL}/health",
                timeout=2.0
            )
            if response.status_code == 200:
                health_data["services"]["notification"] = "connected"
            else:
                health_data["services"]["notification"] = "degraded"
    except Exception:
        health_data["services"]["notification"] = "disconnected"

    return health_data
