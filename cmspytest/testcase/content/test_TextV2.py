import pytest
import random
from request.content.content import content
from conf.config import MyRequest

class Testcontent(content,MyRequest):
    def setup_class(self):
        pass

    def teardown_class(self):
        pass

    @pytest.mark.parametrize('data', MyRequest.dataini("contentv2text_get", MyRequest.dataini(),
                                                       "\\testcase\\content\\data_test.ini"))
    def test_contentv2text_get(self,data,cmongodb):
        params = {"contentDataIds":data}
        response = super().contentv2text_get(params=params)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        # monogodb数据验证
        while len(response['data']):
            sqldict = {"content_data_id": data,"is_deleted" : False}
            getcode = super().Review_mongodb_find(cmongodb[0], "text", sqldict)
            assert response['data'][0]['storageId'] == getcode[0]['_id'] \
                   and response['data'][0]['textValue'] == getcode[0]['text_value'] \
                   and response['data'][0]['textType'] == getcode[0]['text_type']
            break
        print("content_data_id,text_value,textType 验证OK")

    @pytest.mark.parametrize('data', MyRequest.dataini("contentv2text_post", MyRequest.dataini(),
                                                       "\\testcase\\content\\data_test.ini"))
    def test_contentv2text_post(self,data,cmongodb):
        response = super().contentv2text_post(json = data)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        # monogodb数据验证
        while len(response['data']):
            c = [x for x in data['values'] if x in set(MyRequest.dataini('inappropriateWords','iwords'))]
            print("被检测的不恰当词汇：",c)
            if c == []:
                sqldict = {"content_data_id": response['data']['uploadedText'][0]['contentDataId']}
                getcode = super().Review_mongodb_find(cmongodb[0], "text", sqldict)
                assert getcode[0]['text_value'] in data['values'] and getcode[0]['text_type'] == data['textType']
                return response['data']['uploadedText'][0]['contentDataId']
            else:
                assert response['data']['failedUploadedText'][0]['textValue'] in c
            print("values,textType 验证OK")
            # return response['data']['uploadedText'][0]['contentDataId']
            break

    @pytest.mark.parametrize('data', MyRequest.dataini("contentv2text_post",
                                                       MyRequest.dataini(),"\\testcase\\content\\data_test.ini")[:1])
    def test_contentv2text_del(self, data, cmongodb):
        print(data)
        data1 = self.test_contentv2text_post(data,cmongodb)
        print(data1,"data1******")
        params = {"contentDataIds": data1}
        response = super().contentv2text_del(params=params)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        # monogodb数据验证
        while response['data']:
            sqldict = {"content_data_id": data1, "is_deleted": True}
            getcode = MyRequest.Review_mongodb_find(cmongodb[0], "text", sqldict)
            if getcode:
                assert data1 in response['data']['success']
            else:
                assert data1 in response['data']['failed']
            break
        print('monogodb验证OK')

    @pytest.mark.parametrize('data', MyRequest.dataini("text", 'textType',"\\testcase\\content\\data_test.ini"))
    def test_contentv2moderate_put(self,data):
        params = {"textType": data}
        keywordstr = MyRequest.dataini("text", 'keywordstr', "\\testcase\\content\\data_test.ini")
        json = keywordstr[random.randint(0,len(keywordstr)-1)]
        print(data, json)
        response = super().contentv2moderate_put(params=params,json=json)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        while response['data']:
            iwords = MyRequest.dataini("inappropriateWords", 'iwords',"\\conf\\config.ini")
            for i in iwords:
                if i in json:
                    type = 1
                    break
                else:
                    type = 0

            if not type:
                assert str(response['data']['result'])== "True" and response['data']['offensive_sentences'] == []
            else:
                assert str(response['data']['result']) == "False" and response['data']['offensive_sentences'] != []
            break
        print('inappropriateWords检测正常')

    @pytest.mark.parametrize('data', MyRequest.dataini("text", 'textType', "\\testcase\\content\\data_test.ini"))
    def test_contentv2moderate_texts_put(self, data):
        params = {"textType": data}
        keywordstr = MyRequest.dataini("text", 'keywordlist', "\\testcase\\content\\data_test.ini")
        json = keywordstr[random.randint(0, len(keywordstr) - 1)]
        print(data, json)
        response = super().contentv2moderate_texts_put(params=params, json=json)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        while response['data']:
            iwords = MyRequest.dataini("inappropriateWords", 'iwords',"\\conf\\config.ini")
            for i in iwords:
                if i in str(json):
                    typew = 1
                    break
                else:
                    typew = 0

            if not typew:
                assert str(response['data'][0]['result'])== "True" and response['data'][0]['offensive_sentences'] == []
            else:
                assert str(response['data'][0]['result']) == "False" and response['data'][0]['offensive_sentences'] != []
            break
        print('inappropriateWords检测正常')

    @pytest.mark.parametrize('data', MyRequest.dataini("text", 'inappropriateWordReplacement', "\\testcase\\content\\data_test.ini"))
    def test_contentv2sanitize_put(self,data):
        params = {"inappropriateWordReplacement": data}
        keywordstr = MyRequest.dataini("text", 'keywordstr', "\\testcase\\content\\data_test.ini")
        json = keywordstr[random.randint(0, len(keywordstr) - 1)]
        print(data, json)
        response = super().contentv2sanitize_put(params=params, json=json)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        while response['data']:
            iwords = MyRequest.dataini("inappropriateWords", 'iwords',"\\conf\\config.ini")
            for i in iwords:
                if i in json:
                    typew = 1
                    break
                else:
                    typew = 0

            if not typew:
                assert response['data']['inappropriateWords'] == []
            else:
                assert response['data']['inappropriateWords'] != []
            break
        print('inappropriateWords检测正常')

    @pytest.mark.parametrize('data', MyRequest.dataini("contentv2batch_sanitize_post", 'text',
                                                       "\\testcase\\content\\data_test.ini"))
    def test_contentv2batch_sanitize_post(self,data):

        iwr = MyRequest.dataini("text", 'inappropriateWordReplacement_bs', "\\testcase\\content\\data_test.ini")
        iwr = iwr[random.randint(0, len(iwr) - 1)]
        params = {"inappropriateWordReplacement": iwr}
        print(data, iwr)
        response = super().contentv2batch_sanitize_post(params=params, json=data)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        while response['data']:
            iwords = MyRequest.dataini("inappropriateWords", 'iwords',"\\conf\\config.ini")
            for i in iwords:
                if i in data[0]['textValue']:
                    typew = 1
                    break
                else:
                    typew = 0

            if not typew:
                assert response['data']['sanitizedResult'][0]['sanitizedText'] == data[0]['textValue'] \
                       and response['data']['sanitizedResult'][0]['inappropriateWords'] == []
            else:
                assert response['data']['sanitizedResult'][0]['inappropriateWords'] != []
            break
        print('inappropriateWords检测正常')











