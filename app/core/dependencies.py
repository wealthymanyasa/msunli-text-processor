from fastapi import Depends
from fastapi_limiter.depends import RateLimiter

# Global rate limiter instance that will be set during app startup
rate_limit_dependency = None