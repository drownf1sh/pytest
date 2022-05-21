from functools import wraps

def 装饰器(func):    #写装饰器
    @wraps(func)    #使用装饰器修复技术
    def inner(*args,**kwargs):
        print('函数之前执行的代码')
        func(*args,**kwargs)
        print('函数之后执行的代码')
    return inner

@装饰器     #加装饰器
def outer(a):
    '''
    函数的作用注释：被修饰的原函数
    :param a:参数a解释
    :return:函数返回值解释
    '''
    def inner():
        print('内部函数',a)
    return inner()

outer('你好')

print("打印函数名称:",outer.__name__)   #打印函数名称
print('打印函数注释:',outer.__doc__)   #打印函数注释