# import the necessary packages
from threading import Thread
import requests, time, json
import pandas as pd
import random, itertools
import csv

list_a = []
df = pd.read_csv(r'C:\Users\Willy Wang\Desktop\GCS.csv')
print(list(df['url']))
for i in list(df['url']):
    if "tst02" in i:
        print(i)
        a = i.split('.')[-1]
        if a not in list_a:
            list_a.append(a)
print(list_a)




# csvFile = open(r'C:\Users\Willy Wang\Desktop\baidu.csv', "r")
# reader = csv.reader(csvFile)
# with open(r'C:\Users\Willy Wang\Desktop\baidui.csv', "r") as csvFile:
#     reader = csv.reader(csvFile)
#     print(list(reader))
#     for i in reader:
#         print(i)
# # result = []
# for item in reader:
#     Term = item[0].split(',')[0]
#     result.append(Term)
# csvFile.close()
# # print(result)
