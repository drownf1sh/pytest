import os
import random
import pytest
import json
from request.content.content import content
from configobj import ConfigObj
from common.parseconfig import file_name
from conf.config import MyRequest

class Testcontent(content):
    def setup_class(self):
        pass

    def teardown_class(self):
        pass

    @pytest.mark.parametrize('data',MyRequest.dataini("contentv2_get",MyRequest.dataini(),
                                                      "\\testcase\\content\\data_test.ini"))
    def test_contentv2_get(self,data,cmongodb):
        response = super().contentv2_get(params=data)
        assert response['message']== 'Succeeded'
        print('msg验证ok')

        # monogodb数据验证
        while len(response['data']):
            # print(len(response['data']))
            sqldict = {"_id":response['data'][random.randint(0, len(response['data']))-1]['contentDataId']}
            getcode = MyRequest.Review_mongodb_find(cmongodb[0],"content",sqldict)
            # print(getcode)
            assert len(getcode)>0
            assert getcode[0]['client_id'] == data['clientId']and getcode[0]['source_id'] == data['sourceId'] \
                   and getcode[0]['user_id'] == data['userId'] and getcode[0]['content_type'] == data['contentType'] \
                   and getcode[0]['is_active'] == data['isActive'],"monogodb验证异常"
            print("clientId，sourceId验证OK")
            break

    @pytest.mark.parametrize('file', file_name('file')[2][10:11])
    def test_uploadFilesToGcs_post(self,file,cmongodb):
        if file == "document01.txt":
            jsonfile = "test02.json"
        else:
            jsonfile = file_name('json')[2][random.randint(0,3)]
        print(file,jsonfile)
        response = super().contentv2uploadFilesToGcs_post(jsonfile,file)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')
        print(response['data']['uploadedFiles'][0]['url'])

        # 接口返回验证
        curpath = os.path.abspath('.')
        conf_ini = curpath + "\\conf\\config.ini"
        data = ConfigObj(conf_ini, encoding='UTF8')
        uploadfiles = data['uploadfiles']

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
            elif filetype in uploadfiles['PHOTO'] and jsonfile == "test03.json" \
                    and file not in ['iamge02.jpeg','iamge04.gif']:
                assert urltype == "jpg"
            elif (filetype not in uploadfiles['VIDEO'] and jsonfile != "test03.json")\
                    or file in ['iamge02.jpeg','iamge04.gif']:
                assert urltype == filetype
            print("url和fileType验证OK")

        # monogodb数据验证
            sqldict = {"_id": response['data']['uploadedFiles'][0]['contentDataId']}
            getcode = MyRequest.Review_mongodb_find(cmongodb[0], "content", sqldict)
            assert getcode[0]['content_type']== response['data']['uploadedContent'][0]['contentType'] \
                   and getcode[0]['file_type'] == response['data']['uploadedContent'][0]['fileType']
            print("mongodb验证OK")
            return response['data']['uploadedFiles'][0]['contentDataId']

    @pytest.mark.parametrize('data',MyRequest.dataini("contentId_get",MyRequest.dataini(),
                                                      "\\testcase\\content\\data_test.ini"))
    def test_contentv2url_generation_contentId_get(self,data,cmongodb):
        response = super().contentv2url_generation_contentId_get(data)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        # monogodb数据验证
        sqldict = {"_id": data,"is_deleted" : False}
        getcode = MyRequest.Review_mongodb_find(cmongodb[0], "content", sqldict)
        filetype = response['data']['url'].split('.')[-1]
        assert getcode[0]['file_type'] == filetype == response['data']['fileType']
        print("mongodb验证OK")

    @pytest.mark.parametrize('data',MyRequest.dataini("contentId_get",MyRequest.dataini(),
                                                      "\\testcase\\content\\data_test.ini"))
    def test_contentv2contentDataId_get(self,data,cmongodb):
        response = super().contentv2contentDataId_get(data)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        # monogodb数据验证
        sqldict = {"_id": data, "is_deleted": False}
        getcode = MyRequest.Review_mongodb_find(cmongodb[0], "content", sqldict)
        assert getcode[0]['content_type'] == response['data']['contentType'] and getcode[0]['file_type']==response['data']['fileType']\
               and getcode[0]['user_id'] == response['data']['userId']
        print("mongodb验证OK")

    @pytest.mark.parametrize('data',MyRequest.dataini("contentId_get",MyRequest.dataini(),
                                                      "\\testcase\\content\\data_test.ini"))
    def test_contentv2privatecontentDataId_get(self,data,cmongodb):
        response = super().contentv2private_contentDataId_get(data)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        # monogodb数据验证
        sqldict = {"_id": data, "is_deleted": False}
        getcode = MyRequest.Review_mongodb_find(cmongodb[0], "content", sqldict)
        assert getcode[0]['content_type'] == response['data']['contentType'] and getcode[0]['file_type'] == \
               response['data']['fileType'] \
               and getcode[0]['user_id'] == response['data']['userId']
        print("mongodb验证OK")

    @pytest.mark.parametrize('data',MyRequest.dataini("contentId_get",MyRequest.dataini(),
                                                      "\\testcase\\content\\data_test.ini"))
    def test_contentv2privateurlgeneration_contentDataId_get(self,data,cmongodb):
        response = super().contentv2privateurlgeneration_contentDataId_get(data)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        # monogodb数据验证
        sqldict = {"_id": data, "is_deleted": False}
        getcode = MyRequest.Review_mongodb_find(cmongodb[0], "content", sqldict)
        filetype = response['data']['url'].split('.')[-1]
        assert getcode[0]['file_type'] == filetype == response['data']['fileType']
        print("mongodb验证OK")

    @pytest.mark.parametrize('data',MyRequest.dataini("imageUrl",MyRequest.dataini(),
                                                      "\\testcase\\content\\data_test.ini"))
    def test_contentv2transferWebp2Png(self,data):
        print(data)
        response = super().contentv2transferWebp2Png(data)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

    @pytest.mark.parametrize('file',file_name('file')[2][10:11])
    def test_uploadFilesToYoutube_post(self, file, cmongodb):
        if file.count('document') or file.count('iamge'):
            pytest.skip()
        jsonfile = file_name('json')[2][random.randint(0, 3)]
        print(jsonfile)
        response = super().uploadFilesToYoutube_post(jsonfile, file)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        while response['data']:
            # monogodb数据验证
            urltype = response['data']['uploadedFiles'][0]['url'].split('.')[-1]
            sqldict = {"_id": response['data']['uploadedFiles'][0]['contentDataId']}
            getcode = MyRequest.Review_mongodb_find(cmongodb[0], "content", sqldict)
            assert getcode[0]['content_type'] == response['data']['uploadedContent'][0]['contentType'] =="VIDEO" \
                   and getcode[0]['file_type'] == response['data']['uploadedContent'][0]['fileType'] ==urltype =="mp4"
            print("mongodb验证OK")
            return response['data']['uploadedFiles'][0]['contentDataId']

    @pytest.mark.parametrize('file', file_name('file')[2][10:12])
    def test_deleteFiles_contentIds_del(self,file,cmongodb):
        contentDataId_1 = self.test_uploadFilesToGcs_post(file,cmongodb)
        print('---------------test_uploadFilesToGcs_post-----------')
        contentDataId_2 = self.test_uploadFilesToYoutube_post(file,cmongodb)
        print('---------------test_uploadFilesToYoutube_post-----------')
        data = '{"userId":"test01","clientId":"fgm","sourceId":"test01","clientName":"test01","sourceType":"test01"}'
        response = super().deleteFiles_contentIds_del(data,contentDataId_1,contentDataId_2)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        while response['data']:
            for i in range(len(response['data']['success'])):
                sqldict = {"_id": response['data']['success'][i]}
                getcode = MyRequest.Review_mongodb_find(cmongodb[0], "content", sqldict)
                assert str(getcode[0]['is_deleted']) == str(True)
            print("mongodb验证OK")
            break








