import yaml
import requests

yaml_path = r'C:\wqw\Git\cmsunittest\yaml\ContentApi\content\V2.yaml'

def read_yaml(yaml_path):
    with  open(yaml_path, 'r', encoding="utf-8") as file:
        yaml_data = yaml.load(file,yaml.FullLoader)
        return yaml_data

all_data = read_yaml(yaml_path)
pdata = ['0','0','0','PHOTO',None]
domain = 'https://mik.qa.platform.michaels.com/api/cms'
rtype = all_data['args'][0]
url = domain + all_data['args'][1]
headers = {'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJjbGllbnRJZCI6InVzciIsIl91c2VySWQiOiI2OTE4MDMxNTA0NjMyNjIyNDA1IiwiX3NlbGxlclN0b3JlSWQiOm51bGwsIl9kZXZpY2VVdWlkIjoiZDUyMGM3YTgtNDIxYi00NTYzLWI5NTUtZjVhYmM1NmI5N2VjIiwiX2RldmljZU5hbWUiOiJDaHJvbWUiLCJfY3JlYXRlVGltZSI6IjE2NDQzNzYzMTUwNzciLCJfZXhwaXJlVGltZSI6IjE2NDY5NjgzMTUwNzciLCJzdWIiOiI2OTE4MDMxNTA0NjMyNjIyNDA1IiwiaWF0IjoxNjQ0Mzc2MzE1LCJleHAiOjE2NDY5NjgzMTUsImF1ZCI6InVzZXIiLCJqdGkiOiJMWVNOaXQ5WHBFakFDV3R3WldlalRsMmU5MFdGR013cCJ9.HIltIL-S1TazbgP8iouPfJHSsHri5xilyQSRKf5xjFmJelGGb7Fl9Up_29zYOTTeN_qS18szQv12B9bF98ossg'}
params = all_data['kwargs'][0]['params']
j = 0
for i in params:
    params[i] = pdata[j]
    j +=1
print(params)
response = requests.request(rtype, url, headers=headers, params=params)
print(response.text)