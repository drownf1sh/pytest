from threading import Thread,Lock
import random
lock = Lock()
class test_a():
    @classmethod
    def test_a_01(self,a,b):
        return a*b

class Test(Thread):
    list_t = []
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        with lock:
            Test.list_t.append(test_a.test_a_01(random.randint(1,10),random.randint(1,10)))

if __name__ == '__main__':
    t_arry=[]
    for i in range(10):
        t = Test()
        t_arry.append(t)
        t.start()

    for t in t_arry:
        t.join()
    print('done')
    print(Test.list_t)