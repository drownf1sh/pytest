import unittest
import datetime
from BeautifulReport import BeautifulReport
import test_calculator

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.discover('.', pattern='test00.py')
    # suite = unittest.TestSuite()
    # suite.addTest(test_calculator.TestCalculator('test_add'))
    # suite.addTest(test_calculator.TestCalculator('test_mul'))
    result = BeautifulReport(suite)

    curtime =  datetime.datetime.now().strftime("%y_%m_%d")
    report = 'TestReport_' + curtime
    result.report(filename= report, description='测试deafult报告', log_path='report')

