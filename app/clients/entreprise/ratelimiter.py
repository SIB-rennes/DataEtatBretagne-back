import redis
from datetime import datetime

from pyrate_limiter import Limiter, RedisBucket, RequestRate
from .models.config import Config

API_ENTREPRISE_RATELIMITER_ID = "api_entreprise"

def _make_ratelimiter(conf: Config):
    redis_pool = redis.ConnectionPool(
        host=conf.rate_limiter.redis.host,
        port=conf.rate_limiter.redis.port,
        db=conf.rate_limiter.redis.db,
    )
    rates = [
        RequestRate(
            conf.rate_limiter.limit,
            conf.rate_limiter.duration,
        )
    ]

    return Limiter(
        *rates,
        bucket_class=RedisBucket,
        bucket_kwargs={
            "bucket_name": API_ENTREPRISE_RATELIMITER_ID,
            "expire_time": rates[-1].interval,
            "redis_pool": redis_pool,
        },
        time_function=lambda: datetime.utcnow().timestamp(),
    )