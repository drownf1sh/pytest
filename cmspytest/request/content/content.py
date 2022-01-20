import os
import demjson
from conf import config
import requests
from configobj import ConfigObj
from common.parseconfig import fileuploadparameter

class content(object):

    def __init__(self):
        # 当前路径针对于run.py文件来说
        curpath = os.path.abspath('.')
        conf_ini = curpath + "\\conf\\config.ini"
        # conf_ini = r"C:\Users\Willy Wang\PycharmProjects\cmspytest\conf\config.ini"
        cfig = ConfigObj(conf_ini, encoding='UTF8')
        self.env = cfig['env']['env']
        self.Authorization = cfig['env']['Authorization']
        self.domain = "https://cms." + self.env + ".platform.michaels.com"

    def contentv2_get(self,params):
        """GET /content​/v2"""
        url = self.domain + "/api/content/v2"
        headers = {'Authorization':self.Authorization}
        response = requests.request("GET", url, params=params, headers=headers)
        return response.json()

    def contentv2text_post(self,json):
        """POST /content​/v2​/text"""
        url = self.domain + "/api/content/v2/text"
        response = requests.request("POST", url,json=json)
        return response.json()

    def contentv2uploadFilesToGcs_post(self,jsonname,*args):
        """
        POST /content/v2/uploadFilesToGcs
        Document：txt,pdf
        Image：jpg,jpeg,png,gif,jpe,jif,jfif,jfi
        Video：webm,mpg,mp2,mpeg,mpe,mpv,ogg,mp4,m4p,m4v,avi,wmv,asf,mov,qt,flv,swf,avchd,m3u8,ts,3gp,x-matroska
        [ 传一个json，和至少一个文件（document，image，video）]
        """
        url = "https://cms." + self.env + ".platform.michaels.com/api/content/v2/uploadFilesToGcs"
        type0 = fileuploadparameter(jsonname)
        filepath0 = r"C:\Users\Willy Wang\PycharmProjects\cmspytest\json"+"\\"+jsonname
        filesjson = ('contentRequest', (jsonname, open(filepath0, 'rb'), type0))
        files = [filesjson]
        for i in range(len(args)):
            type = fileuploadparameter(args[i])
            filepath = r"C:\Users\Willy Wang\PycharmProjects\cmspytest\file"+"\\"+args[i]
            filesname1 = ('files', (args[i], open(filepath, 'rb'), type))
            files.append(filesname1)
        response = requests.request("POST", url, files=files)
        print(response.json())
        return response.json()



