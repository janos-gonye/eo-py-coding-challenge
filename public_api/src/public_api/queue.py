"""
Redis and RQ queue initialization.
"""

from redis import Redis
from rq import Queue
from public_api.config import settings

redis_conn = Redis.from_url(settings.redis_url)

queue = Queue(connection=redis_conn)
