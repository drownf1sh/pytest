import unittest
import time

class Test_Baidu(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('------setUpClass-------','\n')
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        print('-----tearDownClass-------','\n')
        time.sleep(1)

    def test01(self):
        self.assertEqual(1,1)
        print('第一个用例')

    def test02(self):
        self.assertEqual(1,1)
        print('第二个用例')

if __name__ == '__main__':
    unittest.main()