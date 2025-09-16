from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
import logging
from redis.asyncio import Redis
from sqlalchemy.orm import Session
from .api.endpoints import router as api_router
from .api.auth import router as auth_router
from .utils.multilang_processor import MultiLanguageProcessor
from .models.base import init_db, engine
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize text processor
text_processor = MultiLanguageProcessor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Multi-Language Text Processor API")
    
    # Initialize database
    try:
        init_db(engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Initialize Redis
    try:
        redis = Redis(host="redis", port=6380, decode_responses=True)
        await FastAPILimiter.init(redis)
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
    
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

# Rate limiting middleware
app.add_middleware(
    RateLimiter,
    calls=100,
    time_window=60
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(api_router, prefix="/api/v1", tags=["text-processing"])

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
        redis = Redis(host="redis", port=6380, decode_responses=True)
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