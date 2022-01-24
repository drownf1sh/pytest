import pytest
from conf.config import MyRequest

@pytest.fixture(scope="session", autouse=True)
def cmongodb():
    """连接mongodb"""
    db, client = MyRequest.mongodbConnect()
    print("连接mongodb")
    yield db,client
    client.close()
    print("断开mongodb")

