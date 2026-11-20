import redis
import json
from typing import Optional

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_from_cache(key: str):
    data = redis_client.get(key)
    return json.loads(data) if data else None

def set_to_cache(key: str, value, expire: int = 3600):
    redis_client.setex(key, expire, json.dumps(value))

def delete_from_cache(key: str):
    redis_client.delete(key)