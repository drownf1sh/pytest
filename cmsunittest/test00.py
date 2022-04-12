import unittest   #单元测试模块
class TestCalc(unittest.TestCase):
    def setUp(self):  #每个用例运行之前运行的
        print('setup是啥时候运行的')

    def tearDown(self): #每个用例运行之后运行的
        print('teardown是啥时候运行的')

    @classmethod
    def setUpClass(cls):  #在所有用例执行之前运行的
        print('我是setUpclass，我位于所有用例的开始')

    @classmethod
    def tearDownClass(cls): #在所有用例都执行完之后运行的
        print('我是tearDownClass，我位于多有用例运行的结束')

    def testcc(self):    #函数名要以test开头，否则不会被执行
        '''这是第一个测试用例'''       #用例描述，在函数下，用三个单引号里面写用例描述
        self.assertEqual(1,1)
        print('第一个用例')

    def testaa(self):
        '''这个是第二个测试用例'''
        self.assertEqual(1,1)
        print('第二个用例')

    def testdd(self):
        '''用例描述3'''
        self.assertEqual(1, 2)
        print('第三个用例')

    @unittest.skip("do't run as not ready")
    def testbb(self):
        '''用例描述4'''
        self.assertEqual(1, 1)
        print('第四个用例')
