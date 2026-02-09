import redis
from app.core.config import settings

HOST = settings.REDIS_NAME
redis_client = redis.Redis(
    host = HOST,
    port=6379,
    db=0,
    decode_responses=False  
)
