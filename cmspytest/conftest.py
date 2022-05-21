# import pytest
# from conf.config import MyRequest

<<<<<<< Updated upstream
"""
autouse设置为True，自动调用fixture功能
Scope:
    session:在一次Run或Debug中执行的所有case共享一个session,第一个case开始执行的时候session开始，
            最后一个case执行结束的时候session结束，这些case可能分布在不同的class或module中。
    module:一个.py文件可以看作一个module，其表示的范围指该文件中第一个case到最后一个case之间的范围
    class:表示的范围即class的范围
    function:表示的范围即function的范围
"""
@pytest.fixture(scope="session", autouse=True)
def cmongodb():
    """连接mongodb"""
    db, client = MyRequest.mongodbConnect()
    print("连接mongodb")
    yield db,client
    client.close()
    print("断开mongodb")
=======
# @pytest.fixture(scope="session", autouse=True)
# def cmongodb():
#     """连接mongodb"""
#     db, client = MyRequest.mongodbConnect()
#     print("连接mongodb")
#     yield db,client
#     client.close()
#     print("断开mongodb")
>>>>>>> Stashed changes


