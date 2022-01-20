import pytest
import time
import os
from configobj import ConfigObj

class DictImporter(object):
    def update_configini(self,str):
        curpath = os.path.abspath('.')
        conf_ini = curpath+"\\conf\\config.ini"
        config = ConfigObj(conf_ini, encoding='UTF8')
        # 读取配置文件
        env = config['env']['env']

        if env==str:
            print("env:", env)
            return env
        else:
            # 修改配置文件
            config['env']['env'] = str
            # 保存配置文件
            config.write()
            env = config['env']['env']
            print("env:", env)
            return env

 # 修改环境变量
env = "tst03"
upenv = DictImporter()
upenv.update_configini(env)
# 设置log输出时间，以命名log文件
# curtime1 = time.strftime('%Y-%m-%d %H %M %S', time.localtime(time.time()))
curtime1 = time.strftime('%Y-%m-%d', time.localtime(time.time()))
logname = "report"+curtime1+".html"

if __name__ == '__main__':
    # pytest.main(["-v","./testcase", "--html=./log/"+logname])
    # pytest.main(["-v", "./testcase/content/test_ContentV2.py::Testcontent::test_uploadFilesToGcs_post", "--html=./log/" + logname])
    pytest.main(["-v","./testcase/review", "--html=./log/"+logname])
    # pytest.main(["-v", "-n 1", "./testcase/review", "--html=./log/" + logname])
