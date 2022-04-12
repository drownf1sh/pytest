## 多进程demo
from apirequest import api
from multiprocessing import Process,Lock

def foo(str1,lock):
    with lock:
        with open("test_process.txt","a",encoding="utf-8")as f:
            f.write(str(str1)+"\n")

if __name__ == "__main__":
    # """1、裸跑"""
    # for i in range(2):
    #     t = Process(target=api.trunpagereview,args=(i+1,))
    #     t.start()

    # """2、等待任务完成后回到主进程,通过调用`Process`对象的`join`方法"""
    # p_array = []
    # for i in range(2):
    #     t = Process(target=api.trunpagereview,args=(i+1,))
    #     p_array.append(t)
    #     t.start()
    #
    # for t in p_array:
    #     t.join()
    # print('done')

    """3、增加互斥锁"""
    p_array = []
    lock = Lock()
    for i in range(2):
        p = Process(target=foo,args=(i,lock))
        p_array.append(p)
        p.start()
    for p in p_array:
        p.join()
    print('done')