# def simple_coro(a):
#     print("初始值 a=", a)
#     b = yield a
#     print("传递值 b=", b)
#     c = yield a + b
#     print("传递值 c=", c)
#
# coro = simple_coro(1)
# print(next(coro))
# print(coro.send(2))
# # print(coro.send(3))   ## 报错
#
# def avgcount():
#     count = 0
#     lenth = 0
#     while True:
#         try:
#             avg = yield count/lenth
#         except ZeroDivisionError:
#             avg = yield 0
#         count += avg
#         lenth += 1
#
# avg = avgcount()
# print(next(avg))
# print(avg.send(2))
# print(avg.send(3))
# print(avg.send(4))
# 递归
# while True:
import time

def ctime(func1):
    def timec(*args,**kwargs):
        atime = time.time()
        result = func1(*args,**kwargs)
        btime = time.time()
        print(btime-atime)
        return result
    return timec

@ctime
def func(n):
    if n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return func(n -3) + func(n - 2) + func(n - 1)

# n = int(input('请输入整数:'))
# print(func(n))
a= time.time()
print(a)
time.sleep(0.5)
b = time.time()
print(time.time(),'\n',b-a)

t = time.strftime("%Y-%m-%d %H:%M:%S")
t1 = time.strptime(t,'%Y-%m-%d %H:%M:%S')
print(type(t),t)
print(type(t1),t1)