import os
import pytest
import time
import json
from request.content import content
from conf import config
from configobj import ConfigObj

# # 环境env
# curpath = os.path.abspath('.')
# conf_ini = curpath + "\\conf\\config.ini"
# # conf_ini = r"C:\Users\Willy Wang\PycharmProjects\cmspytest\conf\config.ini"
# env = ConfigObj(conf_ini, encoding='UTF8')['env']['env']
#
# # 测试数据准备
# data_ini = curpath+"\\testcase\\content\\data_test.ini"
# data = ConfigObj(data_ini, encoding='UTF8')
# data_contentv2text_post = data['contentv2text_post'][env]
# data_contentv2text_post = json.loads(data_contentv2text_post)
#

class Testcontent:

#     def setup_class(self):
#         """连接mongodb"""
#         # global a
#         # a= func_header
#         print ("连接mongodb")
#
#     def teardown_class(self):
#         """断开mongodb"""
#         print ("断开mongodb")
# #
#
#     @pytest.mark.parametrize('data', data_contentv2text_post)
#     def test_01(self,data):
#         print('略***********',data)


# @pytest.fixture(scope="module", autouse=True)
# def mod_header(request):
#     print('\n-----------------')
#     print('module      : %s' % request.module.__name__)
#     print('time        : %s' % time.asctime())
#     print('-----------------')
#
# # @pytest.fixture(scope="function", autouse=True)
# def func_header(request):
#     print('\n-----------------')
#     print('function    : %s' % request.function.__name__)
#     print('time        : %s' % time.asctime())
#     print('-----------------')
#     @pytest.fixture()
#     def dbcontent(self,func_header):
#         global a
#         return func_header
    a = [1,2,3,4,5]
    @pytest.mark.run(order=0)
    @pytest.mark.parametrize('data', a)
    def test_one(self,data):
        time.sleep(1)
        curtime1 = time.strftime('%Y-%m-%d %H %M %S', time.localtime(time.time()))
        print('in test_one()',data,curtime1)

    @pytest.mark.run(order=2)
    def test_two(self):
        time.sleep(1)
        curtime1 = time.strftime('%Y-%m-%d %H %M %S', time.localtime(time.time()))
        print('in test_two()',curtime1)
