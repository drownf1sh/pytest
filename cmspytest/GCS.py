import pandas as pd

df = pd.read_csv(r'C:\Users\Willy Wang\Desktop\GCS.csv')
list_a = list(df['url'])

list_b = []
list_c = []
for i in list_a:
    if i in list_b:
        list_c.append(i)
    else:
        list_b.append(i)

assert list_a == list_b,print('重复数据：',len(list_c),'\n',list_c)

print("总数据：",len(list_a))
print("重复数据统计：",len(list_c))
print('重复数据：',list_c)

