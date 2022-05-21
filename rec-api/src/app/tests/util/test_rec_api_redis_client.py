from unittest import mock

import fakeredis
import pytest
import redis.exceptions

from app.main.util.rec_api_redis_client import rec_api_redis_client
from app.main.util.global_db_connection import redis_client


class TestRedisClient:
    host = "host"
    port = "6379"
    redis_sentinel_port = "1234"
    fake_redis_server = fakeredis.FakeServer()

    @pytest.mark.parametrize(
        "exception",
        [
            redis.connection.ConnectionError,
            redis.exceptions.ConnectionError,
            redis.exceptions.BusyLoadingError,
            redis.exceptions.TimeoutError,
            redis.exceptions.ReadOnlyError,
        ],
    )
    @mock.patch("app.main.util.global_db_connection.redis_client.hget")
    @mock.patch("app.main.util.rec_api_redis_client.rec_api_redis_client.update_host")
    def test_handle_exceptions_wrapper(
        self, mock_handle_exceptions_wrapper, mock_redis_hget, exception
    ):
        mock_handle_exceptions_wrapper.return_value = True
        mock_redis_hget.side_effect = exception
        with pytest.raises(exception):
            rec_api_redis_client.hget("name", "key")

        assert mock_handle_exceptions_wrapper.called

    @mock.patch("app.main.util.global_db_connection.redis_client.delete")
    def test_delete(self, mock_redis_delete):
        mock_redis_delete.return_value = True
        rec_api_redis_client.delete("key")
        assert redis_client.delete.called

    @mock.patch("app.main.util.global_db_connection.redis_client.set")
    def test_set(self, mock_redis_set):
        mock_redis_set.return_value = True
        rec_api_redis_client.set("name", "value")
        assert redis_client.set.called

    @mock.patch("app.main.util.global_db_connection.redis_client.hset")
    def test_hset(self, mock_redis_hset):
        mock_redis_hset.return_value(True)
        rec_api_redis_client.hset("name", "key", "value")
        assert redis_client.hset.called

    @mock.patch("app.main.util.global_db_connection.redis_client.hmset")
    def test_hmset(self, mock_redis_hmset):
        mock_redis_hmset.return_value(True)
        rec_api_redis_client.hmset("name", "key")
        assert redis_client.hmset.called

    @mock.patch("app.main.util.global_db_connection.redis_client.get")
    def test_get(self, mock_redis_get):
        mock_redis_get.return_value(True)
        rec_api_redis_client.get("name")
        assert redis_client.get.called

    @mock.patch("app.main.util.global_db_connection.redis_client.hget")
    def test_hget(self, mock_redis_hget):
        mock_redis_hget.return_value(True)
        rec_api_redis_client.hget("name", "key")
        assert redis_client.hget.called

    @mock.patch("app.main.util.global_db_connection.redis_client.hmget")
    def test_hmget(self, mock_redis_hmget):
        mock_redis_hmget.return_value(True)
        rec_api_redis_client.hmget("name", "key")
        assert redis_client.hmget.called

    @mock.patch("app.main.util.global_db_connection.redis_client.hgetall")
    def test_hgetall(self, mock_redis_hgetall):
        mock_redis_hgetall.return_value(True)
        rec_api_redis_client.hgetall("name")
        assert redis_client.hgetall.called

    @mock.patch("redis.sentinel.Sentinel.discover_master")
    @mock.patch("redis.StrictRedis")
    def test_update_host(self, mock_strict_redis, mock_discover_master):
        mock_discover_master.return_value = ("new_host", "new_port")
        mock_strict_redis.return_value = fakeredis.FakeStrictRedis(
            server=self.fake_redis_server
        )

        rec_api_redis_client.update_host()
        assert mock_discover_master.called
        assert mock_strict_redis.called


if __name__ == "__main__":
    pytest.main()
