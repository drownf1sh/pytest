# import pytest
# from conf import config
#
# # mongodb实例
# configMR = config.MyRequest()
# mgoreview_find = configMR.Review_mongodb_find
#
# @pytest.fixture(scope="session", autouse=True)
# def cmongodb():
#     """连接mongodb"""
#     print ("连接mongodb")
#     mongodb_content = configMR.mongodbConnect
#     db, client = mongodb_content()
#     yield db,client
#     print("断开mongodb")
#     client.close()
#
