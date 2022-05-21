from threading import Thread,Lock
import datetime
import time

class function():
    @classmethod
    def add(self,a,b):
        return a+b

class Test(Thread):
    list_r = []
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        for i in range(3):
            time.sleep(0.5)
            # print(i)
            Test.list_r.append(function.add(i,1))

if __name__=='__main__':
    a1=datetime.datetime.now()
    mutex =Lock()
    t_array = []
    for i in range(10):
        t = Test()
        t_array.append(t)
        t.start()
    for i in t_array:
        t.join()
    print(Test.list_r)
    print(len(Test.list_r))
    a2=datetime.datetime.now()
    print(a1)
    print(a2)
    print(a2-a1)

# a1 = datetime.datetime.now()
# for i in range(10):
#     Test().run()
# a2=datetime.datetime.now()
# print(a1)
# print(a2)
# print(a2-a1)







