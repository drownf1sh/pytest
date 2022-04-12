from myrequest import MyRequest
class api:
    @classmethod
    def trunpagereview(self,num):
        url = 'https://mik.qa.platform.michaels.com/api/cms/rating-review/v2/review/MMAC070229'
        params = {'pageIndex':0,'pageSize':num,'offset':-1,'objectType':0,'reviewSortType':'CREATE_TIME','sortOrder':'DESC','showReply':True}
        response = MyRequest.sendRequest(url,'get',params=params)
        assert response.status_code==200
        return response.json()
