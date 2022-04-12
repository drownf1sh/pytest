import unittest
from calculator import Calculator
import time
import ddt

@ddt.ddt()
class TestCalculator(unittest.TestCase):

    # setup 每个用例都会执行 Fixture
    def setUp(self):
        print("test start")

    # teardrown 每个用例都会执行
    def tearDown(self):
        print("test end")

    @ddt.data(*[(1,2,3),(3,4,7)])
    @ddt.unpack
    def test_add(self,m,n,l):
        """ test_add """
        time.sleep(1)
        c = Calculator(m,n)
        result = c.add()
        self.assertEqual(result,l)

    def test_sub(self):
        """ test_sub """
        c = Calculator(7,2)
        result = c.sub()
        self.assertEqual(result,5)

    def test_mul(self):
        """ test_mul """
        c = Calculator(3,5)
        result = c.mul()
        self.assertEqual(result,15)

    def test_div(self):
        """ test_div """
        c = Calculator(10,5)
        result = c.div()
        self.assertEqual(result,2)

    @ddt.data(*[(1,2,3),(3,4,7),(2,3,5)])
    @ddt.unpack   # 将（m,n,l）分开，分别付给函数里的三个变量
    def test_ddt_01(self,m,n,l):
        """ test_add """
        print("m:",m)
        print("n:", n)
        print("l:", l)
    # m=1,n=2,l=3

    @ddt.data(*[(1,2,3),(3,4,7),(2,3,5)])
    def test_ddt_02(self,m):
        """ test_add """
        print("m:",m)
    # m=(1,2,3)

    @ddt.data([(1,2,3),(3,4,7),(2,3,5)])
    def test_ddt_03(self,m):
        """ test_add """
        print("m:",m)
    # m=[(1,2,3),(3,4,7),(2,3,5)]
