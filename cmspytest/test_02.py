from threading import Thread,Lock
import pytest
import time
import datetime
import functools
class Test_01():
    def add(self,a,b):
        return a+b

    def ctime(fun):
        @functools.wraps(fun)
        def betime(*args,**kwargs):
            a_time=datetime.datetime.now()
            result = fun(*args,**kwargs)
            b_time=datetime.datetime.now()
            print('\n',b_time)
            print('时间差：',b_time-a_time)
            return result
        return betime

    @ctime
    def test_01(self):
        time.sleep(2)
        assert self.add(1,2)==3


    a = [[1,2],[3,4],[5,6]]
    @pytest.mark.parametrize('a,b',a)
    @ctime
    def test_02(self,a,b):
        time.sleep(2)
        assert self.add(a,b)==a+b

    # for i in range(2):
    #     t = Thread(target=test_02,args=())
    #     t.start()
    #     t.start()
    #
    # def test_01(self,a,b):
    #     assert self.add(a,b)==a+b



if __name__ =="__main__":
    a= datetime.datetime.now()
    # pytest.main(["-v","-s","./test_02.py"])
    pytest.main(["-v", "-s", "./test_02.py","-n=2"])
    b = datetime.datetime.now()
    print('costtime:',b-a)

#
# class Test():
#     xx = False
#
#     def __init__(self):
#         pass
#
#     def test(func):
#         def wrapper(self, *args, **kwargs):
#             print(self.xx)
#             return func(self, *args, **kwargs)
#
#         return wrapper
#
#     @test
#     def test_a(self, a, b):
#         print(f'ok,{a} {b}')
#
# print(Test().test_a(1,2))

# def ctime(fun):
#     # @six.wraps(fun)
#     def betime():
#         a_time=datetime.datetime.now()
#         result = fun()
#         b_time=datetime.datetime.now()
#         print(a_time,b_time)
#         print('时间差：',b_time-a_time)
#         return result
#     return betime
# @ctime
# def test_01():
#         time.sleep(2)
#         return 0
#
# print(test_01())