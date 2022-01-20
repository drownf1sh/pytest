import os
import random
import pytest
import json
from request.content import content
from conf import config
from configobj import ConfigObj
from common.parseconfig import file_name

# 环境env
curpath = os.path.abspath('.')
conf_ini = curpath + "\\conf\\config.ini"
# conf_ini = r"C:\Users\Willy Wang\PycharmProjects\cmspytest\conf\config.ini"
env = ConfigObj(conf_ini, encoding='UTF8')['env']['env']

# 测试数据准备
data_ini = curpath+"\\testcase\\content\\data_test.ini"
data = ConfigObj(data_ini, encoding='UTF8')
uploadfiles = data['uploadfiles']
data_contentv2_get = data['contentv2_get'][env]
data_contentv2_get = json.loads(data_contentv2_get)


# 接口以及mongodb请求实例
configMR = config.MyRequest()
requestMR = content.content()
mgoreview_find = configMR.Review_mongodb_find
contentv2_get = requestMR.contentv2_get
contentv2uploadFilesToGcs_post =  requestMR.contentv2uploadFilesToGcs_post

# 上传文件数据准备
files = file_name('file')[2]
jsons = file_name('json')[2]

class Testcontent:
    def setup_class(self):
        pass

    def teardown_class(self):
        pass

    @pytest.mark.parametrize('data', data_contentv2_get)
    def test_contentv2_get(self,data,cmongodb):
        # params = {"clientId": "mik", "sourceId": "mik", "userId": "498078872773861", "contentType": "PHOTO",
        #           "isActive": True}
        response=contentv2_get(params=data)
        # print(response)
        assert response['message']== 'Succeeded'
        print('msg验证ok')

        # monogodb数据验证
        while len(response['data']):
            # print(len(response['data']))
            sqldict = {"_id":response['data'][random.randint(0, len(response['data']))-1]['contentDataId']}
            getcode = mgoreview_find(cmongodb[0],"content",sqldict)
            # print(getcode)
            assert len(getcode)>0
            assert getcode[0]['client_id'] == data['clientId']and getcode[0]['source_id'] == data['sourceId'] and getcode[0]['user_id'] == data['userId'] and getcode[0]['content_type'] == data['contentType'] and getcode[0]['is_active'] == data['isActive'],"monogodb验证异常"
            print("clientId，sourceId验证OK")
            break

    @pytest.mark.parametrize('file', files[:1])
    def test_uploadFilesToGcs_post(self,file,cmongodb):
        if file == "document01.txt":
            jsonfile = "test02.json"
        else:
            jsonfile = jsons[random.randint(0,3)]
        print(file,jsonfile)
        response = contentv2uploadFilesToGcs_post(jsonfile,file)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        # 接口返回验证
        while len(response['data']['uploadedFiles']):
            filetype = file.split('.')[-1]
            assert response['data']['uploadedFiles'][0]['fileName'] == file
            if filetype in uploadfiles['DOCUMENT']:
                assert  response['data']['uploadedContent'][0]['contentType'] == "DOCUMENT"
            elif filetype in uploadfiles['PHOTO']:
                assert  response['data']['uploadedContent'][0]['contentType'] == "PHOTO"
            elif filetype in uploadfiles['VIDEO']:
                assert response['data']['uploadedContent'][0]['contentType'] == "VIDEO"
            print("contentType验证ok",response['data']['uploadedContent'][0]['contentType'])

            urltype = response['data']['uploadedFiles'][0]['url'].split('.')[-1]

            if filetype in uploadfiles['VIDEO']:
                assert urltype == "mp4"
            elif filetype in uploadfiles['PHOTO'] and jsonfile == "test03.json" and file not in ['iamge02.jpeg','iamge04.gif']:
                assert urltype == "jpg"
            elif (filetype not in uploadfiles['VIDEO'] and  jsonfile != "test03.json")or file in ['iamge02.jpeg','iamge04.gif']:
                assert urltype == filetype
            print("url和fileType验证OK")

        # monogodb数据验证
        # while len(response['data']['uploadedFiles']):
            # print(len(response['data']))
            sqldict = {"_id": response['data']['uploadedFiles'][0]['contentDataId']}
            getcode = mgoreview_find(cmongodb[0], "content", sqldict)
            assert getcode[0]['content_type']== response['data']['uploadedContent'][0]['contentType'] and getcode[0]['file_type'] == response['data']['uploadedContent'][0]['fileType']
            print("mongodb验证OK")
            break

