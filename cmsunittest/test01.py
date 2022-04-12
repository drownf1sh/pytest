from myrequest import MyRequest

# --------------------# ## test01----get-------------------------------------------
url = "https://mik.tst.platform.michaels.com/api/cms/content/v2"
params = {"clientId":"fgm","sourceId":"test01","userId":"test01","contentType":"PHOTO","isActive":True}
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJjbGllbnRJZCI6InVzciIsIl91c2VySWQiOiI2OTE4MDMxNTA0NjMyNjIyNDA1IiwiX3NlbGxlclN0b3JlSWQiOm51bGwsIl9kZXZpY2VVdWlkIjoiZDUyMGM3YTgtNDIxYi00NTYzLWI5NTUtZjVhYmM1NmI5N2VjIiwiX2RldmljZU5hbWUiOiJDaHJvbWUiLCJfY3JlYXRlVGltZSI6IjE2NDQzNzYzMTUwNzciLCJfZXhwaXJlVGltZSI6IjE2NDY5NjgzMTUwNzciLCJzdWIiOiI2OTE4MDMxNTA0NjMyNjIyNDA1IiwiaWF0IjoxNjQ0Mzc2MzE1LCJleHAiOjE2NDY5NjgzMTUsImF1ZCI6InVzZXIiLCJqdGkiOiJMWVNOaXQ5WHBFakFDV3R3WldlalRsMmU5MFdGR013cCJ9.HIltIL-S1TazbgP8iouPfJHSsHri5xilyQSRKf5xjFmJelGGb7Fl9Up_29zYOTTeN_qS18szQv12B9bF98ossg',
  'Cookie': 'JSESSIONID=9810A74FDF2C667B845C1C0BC6D05440.84d565cf88bt452'
}
req = MyRequest().sendRequest(url,"get",headers=headers,params=params)
print(req)

# ----------------# ## test02----post:files-----------------------------------------
url = "https://mik.tst.platform.michaels.com/api/cms/content/v2/uploadFilesToGcs"
files=[('files',('iamge01.jpg',open(r'C:/Users/Willy Wang/Desktop/GCS limit file/4rf file/iamge01.jpg','rb'),'image/jpeg')),('contentRequest',('test01.json',open(r'C:/Users/Willy Wang/Desktop/testvideo/test01.json','rb'),'application/json'))]
req = MyRequest().sendRequest(url,"post",files=files)
print(req)

# ----------------# ## test03----post:json-----------------------------------------
url = "https://mik.tst.platform.michaels.com/api/cms/content/v2/text"
json = {
  "clientId": "string",
  "needScreened": True,
  "sourceId": "string",
  "textType": "STORE_NAME",
  "values": [
    "good"
  ]
}
req = MyRequest().sendRequest(url,"post",json=json)
print(req)

# ----------------# ## test04----put:json-----------------------------------------
url = "https://mik.tst.platform.michaels.com/api/cms/content/v2/sanitize"
params = {"inappropriateWordReplacement":"STAR"}
json = "good,fuck"
req = MyRequest().sendRequest(url,"put",params=params,json=json)
print(req)

# ----------------# ## test05----del:params-----------------------------------------
url = "https://mik.tst.platform.michaels.com/api/cms/content/v2/text"
params = {"contentDataIds":"6209399249655496704"}
req = MyRequest().sendRequest(url,"del",params=params)
print(req)

# ----------------# ## test06----del:json-----------------------------------------
content_data = "6224245508488241152,6209773495925800960"
url = "https://mik.tst.platform.michaels.com/api/cms/content/v2/deleteFiles/" + content_data
json = {
  "userId": "test01",
  "clientId": "fgm",
  "sourceId": "test01",
  "clientName": "test01",
  "sourceType": "test01"
}
req = MyRequest().sendRequest(url,"del",json=json)
print(req)




