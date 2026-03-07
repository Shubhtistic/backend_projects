from datetime import datetime, timezone, timedelta

import redis.asyncio as Redis
from typing import Annotated

from app.config import redis_settings

redis_client = Redis.from_url(redis_settings.get_redis_url, decode_responses=True)


async def add_jti_to_blacklist(jti: str, exp: int):
    # imp note: even though we use datetime to generate time and save in exp
    # libraries like jose-python automatically convert to unix time format i.e standard for jwt tokens

    remaining_ttl = exp - int(datetime.now(timezone.utc).timestamp())
    # get the current time and convert to unix timestamp using timestamp()
    if remaining_ttl <= 0:
        # already expired
        return
    await redis_client.set(f"jti:{jti}", "1", ex=remaining_ttl + 1)
    # key   → "jti:abc-123-xyz"  (prefix:actual_jti)
    # value → "1"  (we dont care about value, just existence)
    # ex    → TTL in seconds, Redis auto-deletes after this


async def check_jti_blacklist(jti: str) -> bool:
    res = await redis_client.get(f"jti:{jti}")
    if res is None:
        # not found, not blacklisted
        return False
    return True
