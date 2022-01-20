import logging
import requests
import time
import os
from pymongo import MongoClient
from configobj import ConfigObj

curpath = os.path.abspath('.')
conf_ini = curpath + "\\conf\\config.ini"
# conf_ini = r"C:\Users\Willy Wang\PycharmProjects\cmspytest\conf\config.ini"
configini = ConfigObj(conf_ini, encoding='UTF8')
env = configini['env']['env']
db_cms = "db_cms_" + env
user = configini[db_cms]['user']
pwd = configini[db_cms]['pwd']
id = configini[db_cms]['id']
port = configini[db_cms]['port']
db_name = configini[db_cms]['db_name']

class MyRequest:

    # def __init__(self):
    #     self.env = configini['env']['env']
    #     self.db_cms = "db_cms"+self.env


    def sendRequest(self, url, method, params=None, data=None,
                    headers=None, json=None, cookies=None, timeout=10):
        '''
        :param url: 接口请求地址
        :param method: 接口请求方法：get/post或其他
        :param params: url额外参数，字典或字节流格式（多用于字典格式，字节流的话，多用于文件操作）
        :param data:   字典、字节序列或文件对象（多用于字典）
        :param headers: 请求头信息，字典形式
        :param json:    JSON格式的数据，作为参数传递
        :param cookies:  cookies信息，str类型
        :param  timeout:   设定超时时间，秒为单位
        :return: requests.Response.json()
        '''
        responseResult = None
        new_method = method.lower()
        if new_method == 'get':
            logging.info("正在发送get请求，请求地址：{}， 请求参数{}".format(url, params))
            print("正在发送get请求，请求地址：{}， 请求参数{}".format(url, params))
            responseResult = requests.get(url=url, params=params, headers=headers, timeout=timeout)
        elif new_method == "post":
            print(type(json))
            if json:
                print('json != None')
                logging.info("正在发送请求，请求地址：{}， 请求参数{}".format(url, json))
                responseResult = requests.post(url=url, json=json, headers=headers, cookies=cookies, timeout=timeout)
            else:
                print('json = None')
                logging.info("正在发送请求，请求地址：{}， 请求参数{}".format(url, data))
                responseResult = requests.post(url=url, data=data, headers=headers, cookies=cookies, timeout=timeout)
        # print(MyRequest.config)
        return responseResult.json()

    def mongodbConnect(self):
        """cms_mongodb_connect"""
        time.sleep(1)
        uri = "mongodb://" + user + ":" + pwd + "@" + id + ":" + port + "/?authSource=admin&serverSelectionTimeoutMS=1200"
        client = MongoClient(uri, connect=False)
        db = client.get_database(db_name)
        return db, client

    def Review_mongodb_find(self,db, col, where):
        """Review_mongodb_find"""
        mycol = db[col]
        x = mycol.find(where)
        a = []
        for i in x:
            a.append(i)
        return a