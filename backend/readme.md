### 关于配置 !Important
+ local_settings
请在`AK_Graph_Backend/`文件夹下新建`local_settings.py`

键入配置信息
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": '你的数据库的IP',
        "NAME": '你的数据库',
        "USER": '你的用户名',
        "PASSWORD": '你的密码',
        "PORT": 你的端口号,
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

NEO_DB_POOL = {
    'profile': 'http://localhost:7474',
    'username': '你的数据库名称',
    'password': '你的密码',
    'size': 1
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://你的redisIP:你的redis端口号",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # 链接超时5s
            "SOCKET_CONNECT_TIMEOUT": 5,
            # 读写超时5s
            "SOCKET_TIMEOUT": 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100
            }
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

SESSION_COOKIE_AGE = 60 * 10

BASE_URL = "http://localhost:8000/api"
```