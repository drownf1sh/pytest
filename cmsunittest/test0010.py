import time

class Time():
    def __init__(self,sec):
        time.sleep(2)
        print("__init__:", time.strftime("%Y-%m-%d %H:%M:%S"))
        self.sec = sec

    #声明一个静态类方法
    @staticmethod
    def sec_minutes1(s1,s2):
        time.sleep(2)
        # 不能引用self.sec
        print("sec_minutes1:", time.strftime("%Y-%m-%d %H:%M:%S"))
        return abs(s1 - s2)

    #声明一个静态类方法
    @classmethod
    def sec_minutes2(cls,s1,s2):
        # 在init初始化之前自动定义sec属性的值，未定义之前self.sec也是不能被引用的
        time.sleep(2)
        print("sec_minutes2:", time.strftime("%Y-%m-%d %H:%M:%S"))
        cls.sec = abs(s1-s2)
        return abs(s1-s2)

    # 声明一个属性方法
    @property
    def sec_minutes3(self):
        time.sleep(2)
        print("sec_minutes3:", time.strftime("%Y-%m-%d %H:%M:%S"))
        return 100,self.sec

    # 声明一个普通函数方法
    def sec_minutes4(self,s1):
        time.sleep(2)
        print("sec_minutes4:", time.strftime("%Y-%m-%d %H:%M:%S"))
        return s1,self.sec
print('------------------------------')
print(Time(11).sec_minutes1(10,5))   ## 5
time.sleep(5)
print('------------------------------')
print(Time(11).sec_minutes2(100,5),Time.sec)  ## 95 95
# time.sleep(5)
# print('------------------------------')
# print(Time(10).sec_minutes3)    ## (100, 10)
# time.sleep(5)
# print('------------------------------')
# print(Time(100).sec_minutes4(50))  ## (50, 100)
# time.sleep(5)
# print('------------------------------')
