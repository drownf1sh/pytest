from conf.config import MyRequest
import requests
import os
from common.parseconfig import fileuploadparameter

env = MyRequest.dataini()
Authorization = MyRequest.dataini('env','Authorization')
domain = "https://cms." + env + ".platform.michaels.com"
print(domain,"\n",Authorization)

class content(object):

    def contentv2_get(self,params):
        """GET /content​/v2"""
        url = domain + "/api/content/v2"
        headers = {'Authorization':Authorization}
        response = requests.request("GET", url, params=params, headers=headers)
        return response.json()

    def contentv2text_post(self,json):
        """POST /content​/v2​/text"""
        url = domain + "/api/content/v2/text"
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
        curpath = os.path.abspath('.')
        url = "https://cms." + env + ".platform.michaels.com/api/content/v2/uploadFilesToGcs"
        type0 = fileuploadparameter(jsonname)
        filepath0 = curpath+"\\json\\"+jsonname
        filesjson = ('contentRequest', (jsonname, open(filepath0, 'rb'), type0))
        files = [filesjson]
        for i in range(len(args)):
            type = fileuploadparameter(args[i])
            filepath = curpath+"\\file\\"+args[i]
            filesname1 = ('files', (args[i], open(filepath, 'rb'), type))
            files.append(filesname1)
        response = requests.request("POST", url, files=files)
        print(response.json())
        return response.json()

    def contentv2text_get(self,params):
        """GET /content​/v2​/text"""
        url = domain + "/api/content/v2/text"
        # headers = {'Authorization': Authorization}
        response = requests.request("GET", url, params=params)
        return response.json()

    def contentv2text_del(self,params):
        """ DELETE /content​/v2​/text """
        url = domain + "/api/content/v2/text"
        # headers = {'Authorization': Authorization}
        response = requests.request("DELETE", url, params=params)
        return response.json()

    def contentv2moderate_put(self,params,json):
        """ PUT ​/content​/v2​/moderate """
        url = domain + "/api/content/v2/moderate"
        # headers = {'Authorization': Authorization}
        response = requests.request("PUT", url, params=params,json=json)
        return response.json()

    def contentv2moderate_texts_put(self,params,json):
        """ PUT /content/v2/moderate-texts """
        url = domain + "/api/content/v2/moderate-texts"
        # headers = {'Authorization': Authorization}
        response = requests.request("PUT", url, params=params,json=json)
        return response.json()

    def contentv2sanitize_put(self,params,json):
        """ PUT ​/content​/v2​/sanitize """
        url = domain + "/api/content/v2/sanitize"
        # headers = {'Authorization': Authorization}
        response = requests.request("PUT", url, params=params, json=json)
        return response.json()

    def contentv2batch_sanitize_post(self,params,json):
        """ PPOST ​/content​/v2​/batch-sanitize """
        url = domain + "/api/content/v2/batch-sanitize"
        # headers = {'Authorization': Authorization}
        response = requests.request("POST", url, params=params, json=json)
        return response.json()

    def contentv2url_generation_contentId_get(self,contentId):
        """ GET ​/content​/v2​/url-generation​/{contentId} """
        url = domain + "/api/content/v2/url-generation/"+contentId
        headers = {'Authorization': Authorization}
        response = requests.request("GET", url, headers=headers)
        return response.json()

    def contentv2contentDataId_get(self,contentId):
        """ GET /content/v2/{contentDataId} """
        url = domain + "/api/content/v2/" + contentId
        headers = {'Authorization': Authorization}
        response = requests.request("GET", url, headers=headers)
        return response.json()

    def contentv2private_contentDataId_get(self,contentId):
        """ GET /content/v2/private/{contentDataId} """
        url = domain + "/api/content/v2/private/" + contentId
        # headers = {'Authorization': Authorization}
        response = requests.request("GET", url)
        return response.json()

    def contentv2privateurlgeneration_contentDataId_get(self,contentId):
        """ GET /content/v2/private/url-generation/{contentDataId} """
        url = domain + "/api/content/v2/private/url-generation/" + contentId
        # headers = {'Authorization': Authorization}
        response = requests.request("GET", url)
        return response.json()

    def contentv2transferWebp2Png(self,imageUrl):
        """ GET /content/v2/transferWebp2Png """
        url = domain + "/api/content/v2/transferWebp2Png"
        params = {"imageUrl" : imageUrl}
        # headers = {'Authorization': Authorization}
        response = requests.request("GET", url,params=params)
        return response.json()

    def uploadFilesToYoutube_post(self,jsonname,*args):
        """ POST /content/v2/uploadFilesToYoutube """
        curpath = os.path.abspath('.')
        url = "https://cms." + env + ".platform.michaels.com/api/content/v2/uploadFilesToYoutube"
        type0 = fileuploadparameter(jsonname)
        filepath0 = curpath+"\\json\\"+jsonname
        filesjson = ('contentRequest', (jsonname, open(filepath0, 'rb'), type0))
        files = [filesjson]
        for i in range(len(args)):
            type = fileuploadparameter(args[i])
            filepath = curpath+"\\file\\"+args[i]
            filesname1 = ('files', (args[i], open(filepath, 'rb'), type))
            files.append(filesname1)
        response = requests.request("POST", url, files=files)
        print(response.json())
        return response.json()

    def deleteFiles_contentIds_del(self, json, *args):
        """ DELETE ​/content​/v2​/deleteFiles​/{contentIds} """
        params = args[0]
        for i in range(len(args)):
            if i > 0:
                params = params + "," +args[i]
        headers = {'Content-Type': 'application/json'}
        url = domain + "/api/content/v2/deleteFiles/" + params
        print(url)
        response = requests.request("DELETE", url,  headers=headers,data=json)
        return response.json()






