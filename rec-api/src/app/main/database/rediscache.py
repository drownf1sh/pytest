import redis
import rediscluster
from redis.sentinel import Sentinel
from app.main.configuration.vault_vars_config import (
    REDIS_PASSWORD,
    REDIS_DATABASE,
    REDIS_MODE,
    REDIS_HOST_STR,
    REDIS_PORT,
    REDIS_MASTER,
)


def get_redis_host_port(
    redis_host_str: str, redis_sentinel_port: int, redis_master: str
):
    """
    Gets the master host and port from the redis sentinel
    :param redis_host_str: str A comma separated string of redis sentinel ips
    :param redis_sentinel_port: int A port number for the redis sentinel
    :param redis_master: str A master name for the redis sentinel
    :return: the master redis host and port
    """
    # Get sentinel ip list from redis host string
    r_ip_list = redis_host_str.split(",")
    r_sentinel_ip_list = []
    for r_ip in r_ip_list:
        r_sentinel_ip_list.append((r_ip, redis_sentinel_port))
    r_sentinel = Sentinel(r_sentinel_ip_list)
    # Get the Master from sentinel ip list
    r_host, r_port = r_sentinel.discover_master(redis_master)
    return r_host, r_port


def create_redis_connection():
    if REDIS_MODE == "sentinel":
        redis_host, redis_port = get_redis_host_port(
            REDIS_HOST_STR, REDIS_PORT, REDIS_MASTER
        )

        return redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            password=REDIS_PASSWORD,
            db=REDIS_DATABASE,
            health_check_interval=10,
        )
    elif REDIS_MODE == "cluster":
        redis_start_nodes = [
            dict({"host": host, "port": REDIS_PORT})
            for host in REDIS_HOST_STR.split(",")
        ]
        return rediscluster.RedisCluster(
            startup_nodes=redis_start_nodes, password=REDIS_PASSWORD
        )
    else:
        raise ValueError("The input redis mode is invalid")
