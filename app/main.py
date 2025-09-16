from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
import logging
import os
from redis.asyncio import Redis
from sqlalchemy.orm import Session
from .api.endpoints import router as api_router
from .api.auth import router as auth_router
from .utils.multilang_processor import MultiLanguageProcessor
from .models.base import init_db, engine
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from .core.dependencies import rate_limit_dependency

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize text processor
text_processor = MultiLanguageProcessor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rate_limit_dependency
    # Startup
    logger.info("Starting Multi-Language Text Processor API")
    
    # Initialize database
    try:
        init_db(engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Initialize Redis and rate limiter
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        redis = Redis.from_url(redis_url, decode_responses=True)
        await redis.ping()  # Test the connection
        await FastAPILimiter.init(redis)
        global rate_limit_dependency
        rate_limit_dependency = RateLimiter(times=100, seconds=60)
        logger.info("Redis connection and rate limiter initialized successfully")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        rate_limit_dependency = None
    
    # Test processor initialization
    try:
        test_result = text_processor.tokenize("Mhuri yese yakaungana", language="sn")
        logger.info("Text processor initialized successfully")
    except Exception as e:
        logger.error(f"Processor initialization failed: {e}")
        
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-Language Text Processor API")

app = FastAPI(
    title="Multi-Language Text Processor API",
    description="A FastAPI service for cleaning and tokenizing text in multiple languages",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Rate limiting dependency - configured in lifespan context
rate_limit_dependency = None

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
# Add rate limiting only if Redis is available
router_dependencies = [Depends(oauth2_scheme)]
if rate_limit_dependency:
    router_dependencies.append(Depends(rate_limit_dependency))
app.include_router(api_router, prefix="/api/v1", tags=["text-processing"], dependencies=router_dependencies)

# Log available routes
for route in app.routes:
    logger.info(f"Route: {route.path}, Methods: {route.methods}")

@app.get("/")
async def root():
    return {
        "message": "Multi-Language Text Processor API",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "register": "/auth/register",
                "login": "/auth/token",
                "me": "/auth/users/me"
            },
            "text_processing": {
                "tokenize": "/api/v1/tokenize",
                "batch_tokenize": "/api/v1/tokenize/batch",
                "statistics": "/api/v1/statistics",
            },
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        db = Session(engine)
        db.execute("SELECT 1")
        db_status = True
    except Exception:
        db_status = False
    finally:
        db.close()

    # Test Redis connection
    try:
        redis = Redis.from_url("redis://redis:6379", decode_responses=True)
        await redis.ping()
        redis_status = True
    except Exception:
        redis_status = False

    return {
        "status": "healthy",
        "version": "1.0.0",
        "database_ready": db_status,
        "redis_ready": redis_status,
        "processor_ready": len(text_processor.supported_languages) > 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)