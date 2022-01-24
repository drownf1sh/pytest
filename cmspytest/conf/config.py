import logging
import requests
import time
import os
import json
from pymongo import MongoClient
from configobj import ConfigObj

class MyRequest:

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
        return responseResult.json()

    @classmethod
    def mongodbConnect(self):
        """cms_mongodb_connect"""
        time.sleep(1)
        db_cms = "db_cms_" + self.dataini()
        uri = "mongodb://" + self.dataini(db_cms,'user') + ":" + self.dataini(db_cms,'pwd') \
              + "@" + self.dataini(db_cms,'id') + ":" + str(self.dataini(db_cms,'port')) \
              + "/?authSource=admin&serverSelectionTimeoutMS=1200"
        client = MongoClient(uri, connect=False)
        db = client.get_database(self.dataini(db_cms,'db_name'))
        return db, client

    @classmethod
    def Review_mongodb_find(self,db, col, where):
        """Review_mongodb_find"""
        mycol = db[col]
        x = mycol.find(where)
        a = []
        for i in x:
            a.append(i)
        return a

    # path = "\\config.ini",path="\\conf\\config.ini"
    @classmethod
    def dataini(self,module="env", data="env", path="\\conf\\config.ini"):
        """
        module="env",
        data="env",
        path = "\\conf\\config.ini
        """
        curpath = os.path.abspath('.')
        data_ini = curpath + path
        dataini = ConfigObj(data_ini, encoding='UTF8')
        data = dataini[module][data]
        try:
            json_data = json.loads(data)
            return json_data
        except:
            return data