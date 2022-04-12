import unittest
from calculator import Calculator
import time

class TestCalculator(unittest.TestCase):

    # setup 每个用例都会执行 Fixture
    def setUp(self):
        print("test start")

    # teardrown 每个用例都会执行
    def tearDown(self):
        print("test end")

    def test_add(self):
        """ test_add """
        time.sleep(1)
        c = Calculator(3,5)
        result = c.add()
        self.assertEqual(result,8)

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
