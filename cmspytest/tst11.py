import csv
import random, itertools
# import the necessary packages
from threading import Thread
import requests, time, json
import pandas as pd
import random, itertools

# 读取csv至字典
csvFile = open(r'C:\Users\Willy Wang\Desktop\query_records.csv', "r")
reader = csv.reader(csvFile)

# 建立空字典
result = []
for item in reader:
    # 忽略第一行
    # if reader.line_num == 1:
    #     continue
    # result[item[0]] = item[1]
    Term = item[0].split(',')[0]
    # print(item[0].split(',')[0])
    result.append(Term)
csvFile.close()
print(result)
TEST_SAMPLE_SIZE = 100
input_list = random.sample(result, TEST_SAMPLE_SIZE)
