
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": 'localhost',
        "NAME": 'akgraph',
        "USER": 'j',
        "PASSWORD": 'j',
        "PORT": 3306
    }
}

NEO_DB_POOL = {
    'profile': 'http://localhost:7474',
    'username': 'mydb',
    'password': 'Jzdjzy815926',
    'size': 1
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379",
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
