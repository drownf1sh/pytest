# import requests
# from app.main.configuration.vault_vars_config import INVENTORY_API
#
#
# def filter_no_inventory_items(
#     channel: int,
#     store_id: str,
#     recommendation_list: list,
#     return_number: int,
# ):
#     """
#     This function checks the inventory status of a list of skus and returns the ones with active inventory
#     :param channel: int. The channel number of platform to check for inventory
#     :param store_id: str. The store id of a michaels store, -1 for michaels.com
#     :param recommendation_list: list. recommendation list to be filtered
#     :param return_number: int. number of final recommendation results
#     :return list. The recommendation list after filtering inactive inventory items
#
#     """
#     filter_result = []
#     if len(recommendation_list) == 0:
#         return filter_result
#     base_dict = {"channel": channel, "michaelsStoreId": store_id}
#     data_list = [base_dict]
#     # Creating a data list to send as request body for inventory api
#     data_list = [
#         {**item, "skuNumber": x}
#         for item in data_list
#         for x in recommendation_list
#         if str(x) != "nan"
#     ]
#     response = requests.post(
#         INVENTORY_API,
#         json=data_list,
#     ).json()
#     if response and response["code"] == "200":
#         response_data = response["data"]
#         # Filter by checking boolean inStock for an skuNumber
#         filter_result = [x["skuNumber"] for x in response_data if x["inStock"]]
#     return filter_result[:return_number]
