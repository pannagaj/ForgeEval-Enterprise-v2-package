from redis import Redis
from rq import Queue, Worker
from app.core.config import settings

if __name__ == "__main__":
    connection = Redis.from_url(settings.redis_url)
    Worker([Queue("evaluations", connection=connection)], connection=connection).work()
