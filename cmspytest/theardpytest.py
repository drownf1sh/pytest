# from threading import Thread,Lock
# import pytest
# def add(a,b):
#     return a+b
#
# # def test_01(a,b):
# #     assert add(a,b)==a+b
# a = [[1,2],[3,4],[5,6]]
# @pytest.mark.parametrize('a,b',a)
# def test_02(a,b):
#     assert add(a,b)==a+b
#
# for i in range(2):
#     t = Thread(target=test_02,args=())
#     t.start()


import threading

# 创建全局ThreadLocal对象:
local_school = threading.local()


def process_student():
    print('Hello, %s (in %s)' % (local_school.student, threading.current_thread().name))


def process_thread(name):
    # 绑定ThreadLocal的student:
    local_school.student = name
    process_student()


# t1 = threading.Thread(target=process_thread, args=('Alice',), name='Thread-A')
# t2 = threading.Thread(target=process_thread, args=('Bob',), name='Thread-B')
# t1.start()
# t2.start()
# t1.join()
# t2.join()
# coding=utf-8
############## 共享变量均未加锁，仅用来演示共享问题，未考虑同步问题 ###########
############# 线程的变量共享　#############
import threading
import time

gnum = 1


class MyThread(threading.Thread):
    # 重写 构造方法
    def __init__(self, num, num_list, sleepTime):
        threading.Thread.__init__(self)
        self.num = num
        self.sleepTime = sleepTime
        self.num_list = num_list

    def run(self):
        time.sleep(self.sleepTime)
        global gnum
        gnum += self.num
        self.num_list.append(self.num)
        self.num += 1
        print('(global)\tgnum 线程(%s) id:%s num=%d' % (self.name, id(gnum), gnum))
        print('(self)\t\tnum 线程(%s) id:%s num=%d' % (self.name, id(self.num), self.num))
        print('(self.list)\tnum_list 线程(%s) id:%s num=%s' % (self.name, id(self.num_list), self.num_list))


# if __name__ == '__main__':
#     mutex = threading.Lock()
#     num_list = list(range(5))
#     t1 = MyThread(100, num_list, 1)
#     t1.start()
#     t2 = MyThread(200, num_list, 5)
#     t2.start()



