from dataclasses import dataclass

from . import ContextInfo


@dataclass
class RedisConfig:
    host: str
    port: int
    db: int

@dataclass
class RateLimiterConfig:
    limit: int
    duration: int
    redis: RedisConfig

@dataclass
class Config:
    base_url: str
    token: str
    default_context_info: ContextInfo | None
    rate_limiter: RateLimiterConfig

