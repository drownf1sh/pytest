# import time
# # 闭包
# # 闭包指延申了作用域的函数, 也就是作用域中的`Enclosed`的概念
# def make_averager():
#     series = []
#     def averager(value):
#         series.append(value)
#         total = sum(series)
#         return total / len(series)
#     return averager
#
# # my_avg就是延申了作用域的函数
# # series就是被延申作用域的变量
# my_avg = make_averager()
# print(my_avg(1))
# print(my_avg(2))
#
# # 装饰器
# # - 实现原理
# #   就是闭包, 延申了被装饰函数的作用域, 本质是将函数作为参数传递给一个可调用对象(函数或类)
# # - 目的
# #   增加和扩展可调用对象(函数或类)的行为
# # - 实现一个装饰器
# #   - 通过`@`关键字装饰函数
# def clock_it_deco(func):
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
#         print(f"{func.__name__} execute time: {format(end_time - start_time, '.2f')} s")
#         return result
#     return wrapper
#
# # @other_deco
# @clock_it_deco
# def foo(a, b):
#     count = 1
#     while True:
#         if count > a ** b:
#             break
#         count += 1
#
# foo(10, 5)

# def simple_coro(a):
#     print("初始值 a=", a)
#     b = yield a
#     print("传递值 b=", b)
#     c = yield a + b
#     print("传递值 c=", c)

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

import asyncio
import time
class Response:
    staus_code = 200
async def sim_request(index):
    print(f"模拟发送请求 Index: {index}")
    response = Response()
    # 模拟网络延迟
    # 当前是单线程运行的, 如果调用的是time.sleep(1), 那么这个线程会被阻塞
    # 当前线程被阻塞之后, 不会让渡cpu资源, 异步的效率就不会体现
    await asyncio.sleep(1)
    print(f"request index {index}, response status_code: {response.staus_code}")
    return response.staus_code
# 获取消息队列
loop = asyncio.get_event_loop()
# 包装任务
task_array = []
for i in range(100):
    task_array.append(sim_request(i))

## 循环访问事件来完成异步的消息维护
# loop.run_until_complete(asyncio.wait(task_array))
# 关闭事件循环
# loop.close()

## 小技巧: 获取异步完成之后的所有返回值
result = loop.run_until_complete(asyncio.gather(*task_array))
print(result)
loop.close()