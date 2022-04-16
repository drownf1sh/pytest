from threading import Thread,Lock
import datetime
import time
import pytest
import logging

log = logging.getLogger(__name__)
class  function():
    @classmethod
    def add(self,a,b):
        return a+b

class Test():
    list_r = []

    def test_01(self):
        for i in range(3):
            time.sleep(0.5)
            print(i)
            Test.list_r.append(function.add(i,1))
            print(Test.list_r)
            log.info(Test.list_r)
            assert function.add(i,1)==i+1

    def test_02(self):
        for i in range(5,8):
            time.sleep(0.5)
            print(i)
            Test.list_r.append(function.add(i,2))
            print(Test.list_r)
            log.info(Test.list_r)
            assert function.add(i, 2) == i + 2

if __name__ == '__main__':
    # pytest.main(["-v", "-s","./test_13.py","-n=2"])
    # print(Test.list_r)
    curtime1 = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    logname = "report" + curtime1 + "_" + "test"+ ".html"
    pytest.main([ "-s", "./test_13.py", "-n=2", "--html=./log/" + logname])

# if __name__=='__main__':
#     a1=datetime.datetime.now()
#     mutex =Lock()
#     t_array = []
#     for i in range(10):
#         t = Test()
#         t_array.append(t)
#         t.start()
#     for i in t_array:
#         t.join()
#     print(Test.list_r)
#     print(len(Test.list_r))
#     a2=datetime.datetime.now()
#     print(a1)
#     print(a2)
#     print(a2-a1)

# a1 = datetime.datetime.now()
# for i in range(10):
#     Test().run()
# a2=datetime.datetime.now()
# print(a1)
# print(a2)
# print(a2-a1)






