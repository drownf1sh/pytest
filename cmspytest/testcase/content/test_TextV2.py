import os
import pytest
import json
from request.content import content
from conf import config
from configobj import ConfigObj

# 环境env
curpath = os.path.abspath('.')
conf_ini = curpath + "\\conf\\config.ini"
# conf_ini = r"C:\Users\Willy Wang\PycharmProjects\cmspytest\conf\config.ini"
env = ConfigObj(conf_ini, encoding='UTF8')['env']['env']

# 接口以及mongodb请求实例
configMR = config.MyRequest()
requestMR = content.content()
mgoreview_find = configMR.Review_mongodb_find
contentv2text = requestMR.contentv2text_post

# 不恰当词语检测词汇
words_ini = curpath+ "\\conf\\config.ini"
iwords = ConfigObj(words_ini, encoding='UTF8')
iwords = iwords['inappropriateWords']['iwords']
iwords = json.loads(iwords)

# 测试数据准备
data_ini = curpath+"\\testcase\\content\\data_test.ini"
data = ConfigObj(data_ini, encoding='UTF8')
data_contentv2text_post = data['contentv2text_post'][env]
data_contentv2text_post = json.loads(data_contentv2text_post)

class Testcontent:
    def setup_class(self):
        pass

    def teardown_class(self):
        pass

    @pytest.mark.parametrize('data', data_contentv2text_post)
    def test_contentv2text_post(self,data,cmongodb):
        response = contentv2text(json = data)
        print(response)
        assert response['message'] == 'Succeeded'
        print('msg验证ok')

        # monogodb数据验证
        while len(response['data']):
            # print(len(response['data']))
            c = [x for x in data['values'] if x in set(iwords)]
            print("被检测的不恰当词汇：",c)
            if c == []:
                sqldict = {"content_data_id": response['data']['uploadedText'][0]['contentDataId']}
                getcode = mgoreview_find(cmongodb[0], "text", sqldict)
                assert getcode[0]['text_value'] in data['values'] and getcode[0]['text_type'] ==data['textType']
                break
            else:
                assert response['data']['failedUploadedText'][0]['textValue'] in c
                break
        print("values,textType 验证OK")