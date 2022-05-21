from flask_caching import Cache
from app.main.configuration.vault_vars_config import (
    REDIS_MODE,
    REDIS_HOST_STR,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_DATABASE,
    REDIS_MASTER,
)


if REDIS_MODE == "sentinel":
    cache = Cache(
        config={
            "DEBUG": True,
            "CACHE_TYPE": "RedisSentinelCache",
            "CACHE_DEFAULT_TIMEOUT": 300,
            "CACHE_REDIS_SENTINELS": [
                (host, REDIS_PORT) for host in REDIS_HOST_STR.split(",")
            ],
            "CACHE_REDIS_SENTINEL_MASTER": REDIS_MASTER,
            "CACHE_REDIS_PASSWORD": REDIS_PASSWORD,
            "CACHE_REDIS_DB": REDIS_DATABASE,
        }
    )
    """
    Example for sentinel mode:
    cache = Cache(
        config={"DEBUG": True,
                "CACHE_TYPE": "RedisSentinelCache",
                "CACHE_DEFAULT_TIMEOUT": 300,
                "CACHE_REDIS_SENTINELS": [("10.17.191.23", 26379), ("10.17.191.24", 26379), ("10.17.191.25", 26379)],
                "CACHE_REDIS_SENTINEL_MASTER": "redis-tst02",
                "CACHE_REDIS_PASSWORD": "xxxxxxxxxx",
                "CACHE_REDIS_DB": 0
        }
    )
    """

elif REDIS_MODE == "cluster":
    cache = Cache(
        config={
            "DEBUG": True,
            "CACHE_TYPE": "RedisClusterCache",
            "CACHE_DEFAULT_TIMEOUT": 300,
            "CACHE_REDIS_CLUSTER": ",".join(
                [host + ":" + str(REDIS_PORT) for host in REDIS_HOST_STR.split(",")]
            ),
            "CACHE_REDIS_PASSWORD": REDIS_PASSWORD,
        }
    )
    """
    Example for redis cluster:
        cache = Cache(
            config={"DEBUG": True,
                    "CACHE_TYPE": "RedisClusterCache",
                    "CACHE_DEFAULT_TIMEOUT": 300,
                    "CACHE_REDIS_CLUSTER": "10.108.127.83:6392,10.108.127.86:6392,10.108.127.87:6392,10.108.127.88:6392",
                    "CACHE_REDIS_PASSWORD": REDIS_PASSWORD
                    }
        )
    """
else:
    cache = Cache(
        config={
            "DEBUG": True,
            "CACHE_TYPE": "SimpleCache",
            "CACHE_DEFAULT_TIMEOUT": 300,
        }
    )
