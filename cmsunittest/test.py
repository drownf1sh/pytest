import requests
'''requests的二次封装'''
class RequestHadle:
    def __init__(self):
        #创建session对象
        self.session=requests.session()
    def reques(self,url=None,method=None,params=None,data=None,json=None,**kwargs):
        res=self.session.request(url=url,method=method,params=params,data=data,json=json,**kwargs)
        try:
            return res
        except ValueError as err:
            return "格式不正确{}".format(err)
if __name__ == '__main__':
    url = "http://www.baidu.com"
    method="GET"
    r=RequestHadle().reques(url=url,method=method)
    print(r)
    result=r.text
    print(result)