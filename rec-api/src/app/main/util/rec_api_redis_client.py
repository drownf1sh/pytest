import redis
import logging
from redis.sentinel import Sentinel
from app.main.util.global_db_connection import redis_client
import app.main.util.global_db_connection as db_connection

from app.main.configuration.vault_vars_config import (
    REDIS_HOST_STR,
    REDIS_PORT,
    REDIS_MASTER,
    REDIS_DATABASE,
    REDIS_PASSWORD,
    REDIS_MODE,
)


def handle_exceptions_wrapper(func):
    """
    Redis error handling decorator
    """

    def redis_connection_error_handle(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except redis.exceptions.BusyLoadingError:
            if len(args) > 0:
                logging.warning("Redis BusyLoadingError on " "key: " + args[1])
            else:
                logging.warning("Redis BusyLoadingError.")
        except redis.exceptions.ConnectionError:
            if len(args) > 0:
                logging.warning(
                    "Redis Connection Error occurs while performing changes on "
                    "key: " + args[1]
                )
            else:
                logging.warning("Redis Connection Error.")
        except redis.exceptions.RedisError as e:
            if len(args) > 0:
                logging.warning(
                    "Redis Error occurs while performing changes on " "key: " + args[1]
                )
            else:
                logging.warning("Redis Error:" + e.__class__)

        if REDIS_MODE == "sentinel":
            rec_api_redis_client.update_host()
            return func(*args, **kwargs)

    return redis_connection_error_handle


class rec_api_redis_client:
    def __init__(self):
        self.rec_api_redis_client = redis_client
        self.redis_host_str = REDIS_HOST_STR
        self.redis_sentinel_port = REDIS_PORT
        self.redis_master = REDIS_MASTER
        self.redis_database = REDIS_DATABASE
        self.redis_password = REDIS_PASSWORD

    @handle_exceptions_wrapper
    def delete(self, *names):
        return redis_client.delete(*names)

    @handle_exceptions_wrapper
    def set(self, name, value):
        return redis_client.set(name, value)

    @handle_exceptions_wrapper
    def hset(self, name, key, value, mapping=None):
        return redis_client.hset(name, key, value, mapping)

    @handle_exceptions_wrapper
    def get(self, name):
        return redis_client.get(name)

    @handle_exceptions_wrapper
    def hget(self, name, key):
        return redis_client.hget(name, key)

    @handle_exceptions_wrapper
    def hgetall(self, name):
        return redis_client.hgetall(name)

    @handle_exceptions_wrapper
    def hmget(self, name, keys, *args):
        return redis_client.hmget(name, keys, *args)

    @handle_exceptions_wrapper
    def hmset(self, name, keys):
        return redis_client.hmset(name, keys)

    def update_host(self):
        r_ip_list = self.redis_host_str.split(",")
        r_sentinel_ip_list = []
        for r_ip in r_ip_list:
            r_sentinel_ip_list.append((r_ip, self.redis_sentinel_port))
        sentinel = Sentinel(r_sentinel_ip_list)

        host, port = sentinel.discover_master(self.redis_master)
        redis_params = dict(
            host=host,
            port=port,
            db=self.redis_database,
            password=self.redis_password,
            health_check_interval=10,
        )
        db_connection.redis_client = redis.StrictRedis(**redis_params)


rec_api_redis_client = rec_api_redis_client()
