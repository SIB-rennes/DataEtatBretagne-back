import redis
from datetime import datetime
from flask import current_app
from pyrate_limiter import Limiter, RequestRate, RedisBucket

from api_entreprise import JSON_RESOURCE_IDENTIFIER

def _make_rate_limiter():
    config = current_app.config["API_ENTREPRISE"]

    ratelimiter = config["RATELIMITER"]
    ratelimiter_redis = ratelimiter["REDIS"]

    limit = (ratelimiter["LIMIT"])
    duration = (ratelimiter["DURATION"])

    redis_pool = redis.ConnectionPool(
        host=ratelimiter_redis["HOST"],
        port=ratelimiter_redis["PORT"],
        db=ratelimiter_redis["DB"],
    )

    rates = [RequestRate(limit, duration)]

    return Limiter(
        *rates,
        time_function=lambda: datetime.utcnow().timestamp(),
        bucket_class=RedisBucket,
        bucket_kwargs={
            "bucket_name": JSON_RESOURCE_IDENTIFIER,
            "expire_time": rates[-1].interval,
            "redis_pool": redis_pool,
        }
    )
