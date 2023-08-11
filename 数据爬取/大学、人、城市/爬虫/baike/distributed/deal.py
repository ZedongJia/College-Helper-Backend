import redis
import settings
suffix = '/introDetails'

with open(settings.START_URLS_FILE_PATH, "r", encoding="utf8") as r:
    urls = r.readlines()
urls = [url.strip("\n") + suffix for url in urls]

try:
    client = redis.Redis(host="127.0.0.1", port=6379)
    client.lpush(settings.REDIS_KEY, *tuple(urls))
    client.close()
except Exception as e:
    print(e)
    print("无法连接到Redis")
