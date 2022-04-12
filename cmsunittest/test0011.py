import time
import csv
import pandas
import os

path = os.path.abspath('') +'\\file\\GCS.csv'
print(path)

df = pandas.read_csv(path)
dflist = list(df['url'])
for i in dflist:
    print(i)

with open(path,"w",newline='')as f:
    csvdfw = csv.writer(f)
    csvdfw.writerow(['url'])
    csvdfw.writerow(['https://static.platform.michaels.com/tst02/621...1'])
    csvdfw.writerow(['https://static.platform.michaels.com/tst02/621...2'])

with open(path,"r")as f:
    csvdf = csv.reader(f)
    for i in csvdf:
        print(i)

import json
data = [{"a":"aaa","b":"bbb","c":[1,2,3,(4,5,6)]},33,'tantengvip',True]
data2 = json.dumps(data)
print(data2)
with open('./file/tt.txt','w')as f:
    json.dump(data,f)

with open ('./file/tt.txt',"r")as f:
    data1 = json.load(f)
    print(type(data1))
    for i in data1:
        print(i)