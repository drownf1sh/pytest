## 多线程demo
from apirequest import api
from threading import Thread,Lock
zero = 0
result = []
lock = Lock()
def test_trunpagereview(num):
    """没有互斥锁"""
    response = api.trunpagereview(num)
    result.append(response)
    ## 在进程/线程外添加一个空列表，在调用append，最后可拿到进程/线程的输入结果
    return result

def foo():
    """增加互斥锁，导入Lock包，加互斥锁后，整个进程运行时间明显更长"""
    global zero
    for i in range(10**7):
        with lock:
            zero += 1
            zero -= 1

if __name__ == '__main__':
    # """1、裸跑"""
    # for i in range(10):
    #     t = Thread(target=api.trunpagereview,args=(1,))
    #     t.start()

    """2、等待任务完成后回到主进程,通过调用`Thread`对象的`join`方法"""
    t_array = []
    # 保存当前thread对象
    for i in range(2):
        # t = Thread(target=test_trunpagereview,args=(i+1,))
        t = Thread(target=foo)
        t_array.append(t)
        t.start()

    for t in t_array:
        t.join()
        # 调用join方法回到主进程
    print('done')
    print(zero)

