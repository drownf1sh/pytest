from mongoengine import connect, disconnect
from pymongo import MongoClient
import fakeredis


def create_connection(db_alias=None):
    if db_alias is None:
        connection = connect("testdb", host="mongomock://localhost")
    else:
        connection = connect("testdb", alias=db_alias, host="mongomock://localhost")
    return connection


def disconnection(connection):
    connection.drop_database("testdb")
    disconnect()


def create_local_connection(db_name: str = "test", collection_name: str = "test_col"):
    client = MongoClient("mongodb://localhost:27017/")
    test_db = client[db_name]
    collection = test_db[collection_name]
    return client, collection


def disconnect_local_connection(local_conn):
    local_conn.drop_database("test")
    local_conn.close()


def create_fake_redis_connection():
    """
    Use this function to create fake redis server for pytest

    :return: fake redis server connection
    """
    fake_redis_client = fakeredis.FakeStrictRedis()
    return fake_redis_client
