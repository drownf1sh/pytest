import json
import requests
import sys
import time
from functools import wraps
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from requests.exceptions import ConnectionError

from app.main.configuration.vault_vars_config import GLB_DB_URI, REC_DB_URI, CRM_DB_URI
from app.main.util.rec_api_redis_client import rec_api_redis_client


def test_run_time(func):
    @wraps(func)
    def run_time(*args, **kwargs):
        api_path = args[1]
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            if end_time - start_time > 1:
                print(
                    f"Warning: {api_path} respond time: {str(round(end_time - start_time, 2))} seconds"
                )

            status_code = result.status_code
            if status_code != 200:
                print(f"{api_path} api error. Error code: {status_code}")
        except ConnectionError:
            print(f"ERROR: {api_path} connection error")

    return run_time


class api_test:
    def __init__(self, base_url: str = "http://recapi.dev.platform.michaels.com/"):
        """
        Parameters
        ----------
        base_url: str, default = "http://recapi.dev00.mikdev.io/"
            The base url to run api test. Default is for dev00 environment. You can
            change it to tst00 url and also change the environment vars like REC_DB_URI
            to test tst00 env

        :param base_url:
        """
        self.base_url = base_url
        self.err_msg = ""

    def run_test(self):
        # constant for milliseconds timeout
        server_selection_timeout = 5000
        connect_timeout = 20000

        # mongodb connection
        try:
            rec_mongo_client = MongoClient(
                REC_DB_URI,
                serverSelectionTimeoutMS=server_selection_timeout,
                connectTimeoutMS=connect_timeout,
            )
            rec_db_name = rec_mongo_client.get_database().name
            rec_db_instance = rec_mongo_client[rec_db_name]
        except ServerSelectionTimeoutError:
            self.err_msg = "REC MongoDB Server Selection Timeout Error"
            print(self.err_msg)

        try:
            glb_mongo_client = MongoClient(
                GLB_DB_URI,
                serverSelectionTimeoutMS=server_selection_timeout,
                connectTimeoutMS=connect_timeout,
            )
            glb_db_name = glb_mongo_client.get_database().name
            glb_db_instance = glb_mongo_client[glb_db_name]
        except ServerSelectionTimeoutError:
            self.err_msg = "GLB MongoDB Server Selection Timeout Error"
            print(self.err_msg)

        try:
            crm_mongo_client = MongoClient(
                CRM_DB_URI,
                serverSelectionTimeoutMS=server_selection_timeout,
                connectTimeoutMS=connect_timeout,
            )
            crm_db_name = crm_mongo_client.get_database().name
            crm_db_instance = crm_mongo_client[crm_db_name]
        except ServerSelectionTimeoutError:
            self.err_msg = "CRM MongoDB Server Selection Timeout Error"
            print(self.err_msg)

        # MIK buy_it_again
        user_id = rec_db_instance["mik_buy_it_again_atd"].find_one()["user_id"]
        api_path = "api/rec/michaels/buy_it_again"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # MIK buy_it_again_mpg
        user_id = rec_db_instance["mik_buy_it_again_mpg"].find_one()["user_id"]
        api_path = "api/rec/michaels/buy_it_again_mpg"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # MIK popular_search_keyword
        api_path = "api/rec/michaels/popular_search_keyword"
        self._test_single_api(api_path)

        # MIK rec_for_you_search
        user_id = rec_db_instance["mik_rec_for_you_search"].find_one()["user_id"]
        api_path = "api/rec/michaels/rec_for_you_search"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # MIK event_for_you
        user_id = rec_db_instance["mik_event_for_you"].find_one()["user_id"]
        api_path = "api/rec/michaels/event_for_you"
        params = "?user_id=" + str(user_id) + "&event_type=" + "ONLINE"
        self._test_single_api(api_path, params)

        # MIK popular_item
        api_path = "api/rec/michaels/popular_item"
        self._test_single_api(api_path)

        # MIK featured_category
        user_id = rec_db_instance["mik_featured_category"].find_one()["user_id"]
        api_path = "api/rec/michaels/featured_category"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # MIK people_also_buy
        item_id = rec_db_instance["mik_people_also_buy"].find_one()["item_id"]
        api_path = "api/rec/michaels/people_also_buy"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # MIK people_also_view
        item_id = rec_db_instance["mik_people_also_view"].find_one()["item_id"]
        api_path = "api/rec/michaels/people_also_view"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # MIK popular_category
        api_path = "api/rec/michaels/popular_category"
        self._test_single_api(api_path)

        # MIK popular_clearance_category
        api_path = "api/rec/michaels/popular_clearance_category"
        self._test_single_api(api_path)

        # MIK popular_visited_events
        api_path = "api/rec/michaels/popular_visited_events"
        params = "?event_type=" + "ONLINE"
        self._test_single_api(api_path, params)

        # FGM popular_visited_events
        api_path = "api/rec/mktplace/popular_visited_events"
        params = "?event_type=" + "ONLINE"
        self._test_single_api(api_path, params)

        # MIK related_categories_by_category
        api_path = "api/rec/michaels/related_categories_by_category"
        category_path = rec_db_instance[
            "mik_related_categories_by_category"
        ].find_one()["category_path"]
        params = "?category_path=" + category_path
        self._test_single_api(api_path, params)

        # MIK popular_sale_category
        api_path = "api/rec/michaels/popular_sale_category"
        self._test_single_api(api_path)

        # MIK popular_event
        api_path = "api/rec/michaels/popular_event"
        params = "?event_type=" + "ONLINE"
        self._test_single_api(api_path, params)

        # MIK popular_project
        api_path = "api/rec/michaels/popular_project"
        self._test_single_api(api_path)

        # MIK project_inspiration
        user_id = rec_db_instance["mik_project_inspiration"].find_one()["user_id"]
        api_path = "api/rec/michaels/project_inspiration"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # MIK project_use_this
        item_id = rec_db_instance["mik_project_use_this"].find_one()["item_id"]
        api_path = "api/rec/michaels/project_use_this"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # MIK purchased_together
        item_id = rec_db_instance["mik_purchased_together"].find_one()["item_id"]
        api_path = "api/rec/michaels/purchased_together"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # MIK viewed_together
        item_id = rec_db_instance["mik_viewed_together"].find_one()["item_id"]
        api_path = "api/rec/michaels/viewed_together"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # MIK purchased_and_viewed_together
        item_id = rec_db_instance["mik_purchased_together"].find_one()["item_id"]
        api_path = "api/rec/michaels/purchased_and_viewed_together"
        params = "?item_id=" + str(item_id) + "&view_weight=" + str(5)
        self._test_single_api(api_path, params)

        # # MIK recently_viewed
        # user_id = rec_db_instance["mik_recommended_for_you"].find_one()["user_id"]
        # api_path = "api/rec/michaels/recently_viewed"
        # params = "?user_id=" + str(user_id)
        # self._test_single_api(api_path, params)

        # MIK recently_viewed_streaming
        redis_key_list = list(
            rec_api_redis_client.hgetall("mik_streaming_recently_view").keys()
        )
        api_path = "api/rec/michaels/recently_viewed_streaming"
        if len(redis_key_list) != 0:
            field = redis_key_list[0]
            params = "?user_id=" + field.decode("utf-8")
            self._test_single_api(api_path, params)
        else:
            self.err_msg = f"{api_path} api error. Cannot get redis data from mik_streaming_recently_view"
            print(self.err_msg)

        # MIK recommended_for_you
        user_id = rec_db_instance["mik_recommended_for_you"].find_one()["user_id"]
        api_path = "api/rec/michaels/recommended_for_you"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # MIK seasonal_top_picks
        api_path = "api/rec/michaels/seasonal_top_picks"
        self._test_single_api(api_path)

        # MIK favorite_item_for_you
        user_id = rec_db_instance["mik_favorite_item_for_you"].find_one()["user_id"]
        api_path = "api/rec/michaels/favorite_item_for_you"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # MIK similar_events
        event_id = rec_db_instance["mik_similar_events"].find_one()["event_id"]
        api_path = "api/rec/michaels/similar_events"
        params = "?event_id=" + str(event_id) + "&event_type=" + "ONLINE"
        self._test_single_api(api_path, params)

        # FGM similar_events
        event_id = rec_db_instance["fgm_similar_events"].find_one()["event_id"]
        api_path = "api/rec/mktplace/similar_events"
        params = "?event_id=" + str(event_id) + "&event_type=" + "ONLINE"
        self._test_single_api(api_path, params)

        # MIK similar_items
        redis_key_list = list(rec_api_redis_client.hgetall("mik_similar_items").keys())
        api_path = "api/rec/michaels/similar_items"
        if len(redis_key_list) != 0:
            item_id = redis_key_list[0]
            params = "?item_id=" + item_id.decode("utf-8")
            self._test_single_api(api_path, params)
        else:
            self.err_msg = (
                f"{api_path} api error. Cannot get redis data from mik_similar_items"
            )
            print(self.err_msg)

        # MIK similar_items_for_bundle
        redis_key_list = list(rec_api_redis_client.hgetall("mik_similar_items").keys())
        api_path = "api/rec/michaels/similar_items_for_bundle"

        if len(redis_key_list) >= 2:
            field1 = redis_key_list[0].decode("utf-8")
            field2 = redis_key_list[1].decode("utf-8")
            params = f"?items_id_list={field1}%20{field2}"
            self._test_single_api(api_path, params)
        else:
            self.err_msg = f"{api_path} api error. Cannot get more than 1 data from mik_similar_items"
            print(self.err_msg)

        # MIK shopping_cart_bundle
        purchased_together_items = rec_db_instance["mik_purchased_together"].find()
        items_id = []
        count = 0
        for item in purchased_together_items:
            if count < 2:
                items_id.append(item["item_id"])
                count = count + 1
            else:
                break
        separator = "%20"
        items_id_list = separator.join(items_id)
        api_path = "api/rec/michaels/shopping_cart_bundle"
        params = "?items_id_list=" + items_id_list
        self._test_single_api(api_path, params)

        # FGM shopping_cart_bundle
        purchased_together_items = rec_db_instance["fgm_purchased_together"].find()
        items_id = []
        count = 0
        for item in purchased_together_items:
            if count < 2:
                items_id.append(item["item_id"])
                count = count + 1
            else:
                break
        separator = "%20"
        items_id_list = separator.join(items_id)
        api_path = "api/rec/mktplace/shopping_cart_bundle"
        params = "?items_id_list=" + items_id_list
        self._test_single_api(api_path, params)

        # MIK similar_projects
        external_id = rec_db_instance["mik_similar_projects"].find_one()["external_id"]
        api_path = "api/rec/michaels/similar_projects"
        params = "?external_id=" + str(external_id)
        self._test_single_api(api_path, params)

        # FGM similar_projects
        external_id = rec_db_instance["fgm_similar_projects"].find_one()["external_id"]
        api_path = "api/rec/mktplace/similar_projects"
        params = "?external_id=" + str(external_id)
        self._test_single_api(api_path, params)

        # MIK add_user_defined_trending_now
        category_path = "test_category"
        api_path = "api/rec/michaels/add_user_defined_trending_now"
        sep = "%20"
        rec_item_ids = "257" + sep + "778" + sep + "627" + sep + "595"
        params = "?category_path=" + category_path + "&rec_item_ids=" + rec_item_ids
        self._test_single_api_put(api_path, params)

        # MIK user_defined_trending_now
        category_path = rec_db_instance["mik_user_defined_trending_now"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/michaels/user_defined_trending_now"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # MIK trending_now_model
        category_path = rec_db_instance["mik_trending_now"].find_one()["category_path"]
        api_path = "api/rec/michaels/trending_now_model"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # MIK trending_now
        category_path = rec_db_instance["mik_user_defined_trending_now"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/michaels/trending_now"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # MIK trending_now_all_category
        api_path = "api/rec/michaels/trending_now_all_category"
        params = (
            "?user_defined_trending_now="
            + "mik_user_defined_trending_now"
            + "&trending_now="
            + "mik_trending_now"
            + "&candidate_count="
            + str(5)
        )
        self._test_single_api(api_path, params)

        # MIK search_people_also_buy
        items = rec_db_instance["mik_people_also_buy"].find()
        items_id = []
        count = 0
        for item in items:
            if count < 2:
                items_id.append(item["item_id"])
                count = count + 1
            else:
                break
        separator = "%20"
        items_id_list = separator.join(items_id)
        items_scores = "2" + separator + "3"
        api_path = "api/rec/michaels/search_people_also_buy"
        params = "?items_id_list=" + items_id_list + "&items_scores=" + items_scores
        self._test_single_api(api_path, params)

        # MIK search_rerank
        redis_key_list = list(rec_api_redis_client.hgetall("cbf_item_vector").keys())
        if len(redis_key_list) >= 4:
            field1 = redis_key_list[0].decode("utf-8")
            field2 = redis_key_list[1].decode("utf-8")
            field3 = redis_key_list[2].decode("utf-8")
            field4 = redis_key_list[3].decode("utf-8")
        separator = " "
        items_id_str = separator.join([field1, field2])
        order_history_str = separator.join([field3, field4])
        mimetype = "application/json"
        headers = {"Content-Type": mimetype, "Accept": mimetype}
        api_path = "api/rec/michaels/search_rerank"
        data = {"items_id_list": items_id_str, "order_history_list": order_history_str}
        self._test_single_api_post(api_path, data=json.dumps(data), headers=headers)

        # MIK picks_from_experts
        user_id = rec_db_instance["mik_featured_first_layer_category"].find_one()[
            "user_id"
        ]
        api_path = "api/rec/michaels/picks_from_experts"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # MIK yesterday_popular_item
        api_path = "api/rec/michaels/yesterday_popular_item"
        self._test_single_api(api_path)

        # MIK popular_clearance_item
        api_path = "api/rec/michaels/popular_clearance_item"
        self._test_single_api(api_path)

        # MIK popular_sale_item
        api_path = "api/rec/michaels/popular_sale_item"
        self._test_single_api(api_path)

        # MIK popular_item_by_category
        category_path = rec_db_instance["mik_popular_item_by_category"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/michaels/popular_item_by_category"
        params = "?category_path=" + category_path
        self._test_single_api(api_path, params)

        # MIK streaming_trending_now_list
        # api_path = "api/rec/michaels/streaming_trending_now_list"
        # self._test_single_api(api_path)

        # MIK popular_first_layer_category
        api_path = "api/rec/michaels/popular_first_layer_category"
        self._test_single_api(api_path)

        # MIK similar_items_in_same_store
        item_id = rec_db_instance["ea_same_store_similar_items"].find_one()["item_id"]
        api_path = "api/rec/michaels/similar_items_in_same_store"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # MIK similar_items_by_popularity
        redis_key_list = list(rec_api_redis_client.hgetall("mik_similar_items").keys())
        api_path = "api/rec/michaels/similar_items_by_popularity"
        if len(redis_key_list) != 0:
            item_id = redis_key_list[0]
            params = "?item_id=" + item_id.decode("utf-8")
            self._test_single_api(api_path, params)
        else:
            self.err_msg = (
                f"{api_path} api error. Cannot get redis data from mik_similar_items"
            )
            print(self.err_msg)

        # MIK related_queries_by_query
        item_id = rec_db_instance["mik_related_queries_by_query"].find_one()["query"]
        api_path = "api/rec/michaels/related_queries_by_query"
        params = "?query_keyword=" + str(item_id)
        self._test_single_api(api_path, params)

        # MIK related_queries_by_category
        api_path = "api/rec/michaels/related_queries_by_category"
        category_path = rec_db_instance["mik_related_queries_by_category"].find_one()[
            "category_path"
        ]
        params = "?category_path=" + category_path
        self._test_single_api(api_path, params)

        # MIK related_categories_by_query
        api_path = "api/rec/michaels/related_categories_by_query"
        query_keyword = rec_db_instance["mik_related_categories_by_query"].find_one()[
            "query"
        ]
        params = "?query_keyword=" + query_keyword
        self._test_single_api(api_path, params)

        # MKT add_similar_items_for_new_product
        # sku_number = glb_db_instance["online_product"].find_one()["sku_number"]
        # api_path = "api/rec/mktplace/add_similar_items_for_new_product"
        # params = "?sku_number=" + sku_number
        # try:
        #     result = requests.put(f"{self.base_url}{api_path}{params}")
        #     status_code = result.status_code
        #     if status_code != 200:
        #         self.err_msg = f"{api_path} api error. Error code: {status_code}"
        #         print(self.err_msg)
        # except ConnectionError:
        #     self.err_msg = f"ERROR: {api_path} connection error"
        #     print(self.err_msg)

        # MKT popular_item
        api_path = "api/rec/mktplace/popular_item"
        self._test_single_api(api_path)

        # MKT popular_project
        api_path = "api/rec/mktplace/popular_project"
        self._test_single_api(api_path)

        # MKT trending_project
        api_path = "api/rec/mktplace/trending_project"
        self._test_single_api(api_path)

        # MIK trending_project
        api_path = "api/rec/michaels/trending_project"
        self._test_single_api(api_path)

        # MKT event_for_you
        user_id = rec_db_instance["fgm_event_for_you"].find_one()["user_id"]
        api_path = "api/rec/mktplace/event_for_you"
        params = "?user_id=" + str(user_id) + "&event_type=" + "IN_STORE"
        self._test_single_api(api_path, params)

        # MKT shop_near_you
        zip_code = rec_db_instance["fgm_shop_near_you"].find_one()["zip_code"]
        api_path = "api/rec/mktplace/shop_near_you"
        params = "?zip_code=" + str(zip_code)
        self._test_single_api(api_path, params)

        # MKT add_user_defined_trending_now
        category_path = "test_category"
        api_path = "api/rec/mktplace/add_user_defined_trending_now"
        sep = "%20"
        rec_item_ids = "466" + sep + "3646" + sep + "4145"
        params = "?category_path=" + category_path + "&rec_item_ids=" + rec_item_ids
        self._test_single_api_put(api_path, params)

        # MKT user_defined_trending_now
        category_path = rec_db_instance["fgm_user_defined_trending_now"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/mktplace/user_defined_trending_now"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # MKT trending_now_model
        category_path = rec_db_instance["fgm_trending_now"].find_one()["category_path"]
        api_path = "api/rec/mktplace/trending_now_model"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # MKT trending_now
        category_path = rec_db_instance["fgm_user_defined_trending_now"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/mktplace/trending_now"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # api/rec/mktplace fgm_popular_item_by_store
        store_id = rec_db_instance["fgm_popular_item_by_store"].find_one()["store_id"]
        api_path = "api/rec/mktplace/popular_item_by_store"
        params = "?store_id=" + str(store_id)
        self._test_single_api(api_path, params)

        # MKT popular_item_by_category
        category_path = rec_db_instance["fgm_popular_item_by_category"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/mktplace/popular_item_by_category"
        params = "?category_path=" + category_path
        self._test_single_api(api_path, params)

        # MKT trending_now_all_category
        api_path = "api/rec/mktplace/trending_now_all_category"
        params = (
            "?user_defined_trending_now="
            + "fgm_user_defined_trending_now"
            + "&trending_now="
            + "fgm_trending_now"
            + "&candidate_count="
            + str(5)
        )
        self._test_single_api(api_path, params)

        # # MKT recently_viewed
        # user_id = rec_db_instance["fgm_recommended_for_you"].find_one()["user_id"]
        # api_path = "api/rec/mktplace/recently_viewed"
        # params = "?user_id=" + str(user_id)
        # self._test_single_api(api_path, params)

        # MKT recently_viewed_streaming
        redis_key_list = list(
            rec_api_redis_client.hgetall("fgm_streaming_recently_view").keys()
        )
        api_path = "api/rec/mktplace/recently_viewed_streaming"
        if len(redis_key_list) != 0:
            field = redis_key_list[0]
            params = "?user_id=" + field.decode("utf-8")
            self._test_single_api(api_path, params)
        else:
            self.err_msg = f"{api_path} api error. Cannot get redis data from fgm_streaming_recently_view"
            print(self.err_msg)

        # MKT recommended_for_you
        user_id = rec_db_instance["fgm_recommended_for_you"].find_one()["user_id"]
        api_path = "api/rec/mktplace/recommended_for_you"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # MKT search_term_categories
        search_term = "flower"
        api_path = "api/rec/mktplace/search_term_categories"
        params = "?search_term=" + search_term
        self._test_single_api(api_path, params)

        # MKT similar_items
        redis_key_list = list(rec_api_redis_client.hgetall("fgm_similar_items").keys())
        api_path = "api/rec/mktplace/similar_items"
        if len(redis_key_list) != 0:
            item_id = redis_key_list[0]
            params = "?item_id=" + item_id.decode("utf-8")
            self._test_single_api(api_path, params)
        else:
            self.err_msg = (
                f"{api_path} api error. Cannot get redis data from fgm_similar_items"
            )
            print(self.err_msg)

        # MKT popular_search_keyword
        api_path = "api/rec/mktplace/popular_search_keyword"
        self._test_single_api(api_path)

        # MKT rec_for_you_search
        user_id = rec_db_instance["fgm_rec_for_you_search"].find_one()["user_id"]
        api_path = "api/rec/mktplace/rec_for_you_search"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # MKT search_people_also_buy
        items = rec_db_instance["fgm_people_also_buy"].find()
        items_id = []
        count = 0
        for item in items:
            if count < 2:
                items_id.append(item["item_id"])
                count = count + 1
            else:
                break
        separator = "%20"
        items_id_list = separator.join(items_id)
        items_scores = "2" + separator + "3"
        api_path = "api/rec/mktplace/search_people_also_buy"
        params = "?items_id_list=" + items_id_list + "&items_scores=" + items_scores
        self._test_single_api(api_path, params)

        # MKT search_rerank
        redis_key_list = list(rec_api_redis_client.hgetall("cbf_item_vector").keys())
        if len(redis_key_list) >= 4:
            field1 = redis_key_list[0].decode("utf-8")
            field2 = redis_key_list[1].decode("utf-8")
            field3 = redis_key_list[2].decode("utf-8")
            field4 = redis_key_list[3].decode("utf-8")
        separator = " "
        items_id_str = separator.join([field1, field2])
        order_history_str = separator.join([field3, field4])
        mimetype = "application/json"
        headers = {"Content-Type": mimetype, "Accept": mimetype}
        api_path = "api/rec/mktplace/search_rerank"
        data = {"items_id_list": items_id_str, "order_history_list": order_history_str}
        self._test_single_api_post(api_path, data=json.dumps(data), headers=headers)

        # MKT popular_event
        api_path = "api/rec/mktplace/popular_event"
        params = "?event_type=" + "IN_STORE"
        self._test_single_api(api_path, params)

        # MKT yesterday_popular_item
        api_path = "api/rec/mktplace/yesterday_popular_item"
        self._test_single_api(api_path)

        # MKT favourite item
        api_path = "api/rec/mktplace/favorite_item"
        self._test_single_api(api_path)

        # MKT streaming_trending_now_list
        # api_path = "api/rec/mktplace/streaming_trending_now_list"
        # self._test_single_api(api_path)

        # MKT popular_first_layer_category
        api_path = "api/rec/mktplace/popular_first_layer_category"
        self._test_single_api(api_path)

        # MIK popular_visited_projects
        api_path = "api/rec/michaels/popular_visited_projects"
        self._test_single_api(api_path)

        # MKT popular_visited_projects
        api_path = "api/rec/mktplace/popular_visited_projects"
        self._test_single_api(api_path)

        # MIK popular_visited_items
        api_path = "api/rec/michaels/popular_visited_items"
        self._test_single_api(api_path)

        # MKT popular_visited_items
        api_path = "api/rec/mktplace/popular_visited_items"
        self._test_single_api(api_path)

        # MKT related_categories_by_category
        api_path = "api/rec/mktplace/related_categories_by_category"
        category_path = rec_db_instance[
            "fgm_related_categories_by_category"
        ].find_one()["category_path"]
        params = "?category_path=" + category_path
        self._test_single_api(api_path, params)

        # MKT similar_items_by_popularity
        redis_key_list = list(rec_api_redis_client.hgetall("fgm_similar_items").keys())
        api_path = "api/rec/mktplace/similar_items_by_popularity"
        if len(redis_key_list) != 0:
            item_id = redis_key_list[0]
            params = "?item_id=" + item_id.decode("utf-8")
            self._test_single_api(api_path, params)
        else:
            self.err_msg = (
                f"{api_path} api error. Cannot get redis data from fgm_similar_items"
            )
            print(self.err_msg)

        # MKT related_queries_by_query
        item_id = rec_db_instance["fgm_related_queries_by_query"].find_one()["query"]
        api_path = "api/rec/mktplace/related_queries_by_query"
        params = "?query_keyword=" + str(item_id)
        self._test_single_api(api_path, params)

        # MKT related_queries_by_category
        api_path = "api/rec/mktplace/related_queries_by_category"
        category_path = rec_db_instance["fgm_related_queries_by_category"].find_one()[
            "category_path"
        ]
        params = "?category_path=" + category_path
        self._test_single_api(api_path, params)

        # MKT related_categories_by_query
        api_path = "api/rec/mktplace/related_categories_by_query"
        query_keyword = rec_db_instance["fgm_related_categories_by_query"].find_one()[
            "query"
        ]
        params = "?query_keyword=" + query_keyword
        self._test_single_api(api_path, params)

        # MKT picks_from_experts
        user_id = rec_db_instance["fgm_featured_first_layer_category"].find_one()[
            "user_id"
        ]
        api_path = "api/rec/mktplace/picks_from_experts"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_ent buy_it_again
        user_id = rec_db_instance["b2b_ent_buy_it_again_atd"].find_one()["user_id"]
        api_path = "api/rec/b2b_ent/buy_it_again"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_ent buy_it_again_mpg
        user_id = rec_db_instance["b2b_ent_buy_it_again_mpg"].find_one()["user_id"]
        api_path = "api/rec/b2b_ent/buy_it_again_mpg"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_ent popular_search_keyword
        api_path = "api/rec/b2b_ent/popular_search_keyword"
        self._test_single_api(api_path)

        # b2b_ent rec_for_you_search
        user_id = rec_db_instance["b2b_ent_rec_for_you_search"].find_one()["user_id"]
        api_path = "api/rec/b2b_ent/rec_for_you_search"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_ent featured_category
        user_id = rec_db_instance["b2b_ent_featured_category"].find_one()["user_id"]
        api_path = "api/rec/b2b_ent/featured_category"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_ent people_also_buy
        item_id = rec_db_instance["b2b_ent_people_also_buy"].find_one()["item_id"]
        api_path = "api/rec/b2b_ent/people_also_buy"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # b2b_ent popular_item
        api_path = "api/rec/b2b_ent/popular_item"
        self._test_single_api(api_path)

        # # b2b_ent project_inspiration
        # user_id = rec_db_instance["b2b_ent_project_inspiration"].find_one()["user_id"]
        # api_path = "api/rec/b2b_ent/project_inspiration"
        # params = "?user_id=" + str(user_id)
        # self._test_single_api(api_path, params)

        # b2b_ent project_use_this
        item_id = rec_db_instance["b2b_ent_project_use_this"].find_one()["item_id"]
        api_path = "api/rec/b2b_ent/project_use_this"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # b2b_ent purchased_together
        item_id = rec_db_instance["b2b_ent_purchased_together"].find_one()["item_id"]
        api_path = "api/rec/b2b_ent/purchased_together"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # # b2b_ent recently_viewed
        # user_id = rec_db_instance["b2b_ent_recommended_for_you"].find_one()["user_id"]
        # api_path = "api/rec/b2b_ent/recently_viewed"
        # params = "?user_id=" + str(user_id)
        # self._test_single_api(api_path, params)

        # b2b_ent recently_viewed_streaming
        redis_key_list = list(
            rec_api_redis_client.hgetall("b2b_ent_streaming_recently_view").keys()
        )
        api_path = "api/rec/b2b_ent/recently_viewed_streaming"
        if len(redis_key_list) != 0:
            field = redis_key_list[0]
            params = "?user_id=" + field.decode("utf-8")
            self._test_single_api(api_path, params)
        else:
            self.err_msg = f"{api_path} api error. Cannot get redis data from b2b_ent_streaming_recently_view"
            print(self.err_msg)

        # b2b_ent recommended_for_you
        user_id = rec_db_instance["b2b_ent_recommended_for_you"].find_one()["user_id"]
        api_path = "api/rec/b2b_ent/recommended_for_you"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_ent seasonal_top_picks
        api_path = "api/rec/b2b_ent/seasonal_top_picks"
        self._test_single_api(api_path)

        # b2b_ent similar_items
        redis_key_list = list(rec_api_redis_client.hgetall("b2b_similar_items").keys())
        api_path = "api/rec/b2b_ent/similar_items"
        if len(redis_key_list) != 0:
            item_id = redis_key_list[0]
            params = "?item_id=" + item_id.decode("utf-8")
            self._test_single_api(api_path, params)
        else:
            self.err_msg = (
                f"{api_path} api error. Cannot get redis data from b2b_similar_items"
            )
            print(self.err_msg)

        # b2b_ent add_user_defined_trending_now
        category_path = "test_category"
        api_path = "api/rec/b2b_ent/add_user_defined_trending_now"
        sep = "%20"
        rec_item_ids = "103" + sep + "204" + sep + "538"
        params = "?category_path=" + category_path + "&rec_item_ids=" + rec_item_ids
        self._test_single_api_put(api_path, params)

        # b2b_ent user_defined_trending_now
        category_path = rec_db_instance["b2b_ent_user_defined_trending_now"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/b2b_ent/user_defined_trending_now"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # b2b_ent trending_now_model
        category_path = rec_db_instance["b2b_ent_trending_now"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/b2b_ent/trending_now_model"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # b2b_ent trending_now
        category_path = rec_db_instance["b2b_ent_user_defined_trending_now"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/b2b_ent/trending_now"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # b2b_ent trending_now_all_category
        api_path = "api/rec/b2b_ent/trending_now_all_category"
        params = (
            "?user_defined_trending_now="
            + "b2b_ent_user_defined_trending_now"
            + "&trending_now="
            + "b2b_ent_trending_now"
            + "&candidate_count="
            + str(5)
        )
        self._test_single_api(api_path, params)

        # b2b_ent search_people_also_buy
        items = rec_db_instance["b2b_ent_people_also_buy"].find()
        items_id = []
        count = 0
        for item in items:
            if count < 2:
                items_id.append(item["item_id"])
                count = count + 1
            else:
                break
        separator = "%20"
        items_id_list = separator.join(items_id)
        items_scores = "2" + separator + "3"
        api_path = "api/rec/b2b_ent/search_people_also_buy"
        params = "?items_id_list=" + items_id_list + "&items_scores=" + items_scores
        self._test_single_api(api_path, params)

        # b2b_ent search_rerank
        redis_key_list = list(rec_api_redis_client.hgetall("cbf_item_vector").keys())
        if len(redis_key_list) >= 4:
            field1 = redis_key_list[0].decode("utf-8")
            field2 = redis_key_list[1].decode("utf-8")
            field3 = redis_key_list[2].decode("utf-8")
            field4 = redis_key_list[3].decode("utf-8")
        separator = " "
        items_id_str = separator.join([field1, field2])
        order_history_str = separator.join([field3, field4])
        mimetype = "application/json"
        headers = {"Content-Type": mimetype, "Accept": mimetype}
        api_path = "api/rec/b2b_ent/search_rerank"
        data = {"items_id_list": items_id_str, "order_history_list": order_history_str}
        self._test_single_api_post(api_path, data=json.dumps(data), headers=headers)

        # b2b_edu buy_it_again
        user_id = rec_db_instance["b2b_edu_buy_it_again_atd"].find_one()["user_id"]
        api_path = "api/rec/b2b_edu/buy_it_again"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_edu buy_it_again_mpg
        user_id = rec_db_instance["b2b_edu_buy_it_again_mpg"].find_one()["user_id"]
        api_path = "api/rec/b2b_edu/buy_it_again_mpg"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_edu popular_search_keyword
        api_path = "api/rec/b2b_edu/popular_search_keyword"
        self._test_single_api(api_path)

        # b2b_edu rec_for_you_search
        user_id = rec_db_instance["b2b_edu_rec_for_you_search"].find_one()["user_id"]
        api_path = "api/rec/b2b_edu/rec_for_you_search"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_edu featured_category
        user_id = rec_db_instance["b2b_edu_featured_category"].find_one()["user_id"]
        api_path = "api/rec/b2b_edu/featured_category"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_edu people_also_buy
        item_id = rec_db_instance["b2b_edu_people_also_buy"].find_one()["item_id"]
        api_path = "api/rec/b2b_edu/people_also_buy"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # b2b_edu popular_item
        api_path = "api/rec/b2b_edu/popular_item"
        self._test_single_api(api_path)

        # # b2b_edu project_inspiration
        # user_id = rec_db_instance["b2b_edu_project_inspiration"].find_one()["user_id"]
        # api_path = "api/rec/b2b_edu/project_inspiration"
        # params = "?user_id=" + str(user_id)
        # self._test_single_api(api_path, params)

        # b2b_edu project_use_this
        item_id = rec_db_instance["b2b_edu_project_use_this"].find_one()["item_id"]
        api_path = "api/rec/b2b_edu/project_use_this"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # b2b_edu purchased_together
        item_id = rec_db_instance["b2b_edu_purchased_together"].find_one()["item_id"]
        api_path = "api/rec/b2b_edu/purchased_together"
        params = "?item_id=" + str(item_id)
        self._test_single_api(api_path, params)

        # # b2b_edu recently_viewed
        # user_id = rec_db_instance["b2b_edu_recommended_for_you"].find_one()["user_id"]
        # api_path = "api/rec/b2b_edu/recently_viewed"
        # params = "?user_id=" + str(user_id)
        # self._test_single_api(api_path, params)

        # b2b_edu recently_viewed_streaming
        redis_key_list = list(
            rec_api_redis_client.hgetall("b2b_edu_streaming_recently_view").keys()
        )
        api_path = "api/rec/b2b_edu/recently_viewed_streaming"
        if len(redis_key_list) != 0:
            field = redis_key_list[0]
            params = "?user_id=" + field.decode("utf-8")
            self._test_single_api(api_path, params)
        else:
            self.err_msg = f"{api_path} api error. Cannot get redis data from b2b_edu_streaming_recently_view"
            print(self.err_msg)

        # b2b_edu you_may_also_buy
        user_id = rec_db_instance["b2b_edu_you_may_also_buy"].find_one()["user_id"]
        api_path = "api/rec/b2b_edu/you_may_also_buy"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_ent you_may_also_buy
        user_id = rec_db_instance["b2b_ent_you_may_also_buy"].find_one()["user_id"]
        api_path = "api/rec/b2b_ent/you_may_also_buy"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # michaels you_may_also_buy
        user_id = rec_db_instance["mik_you_may_also_buy"].find_one()["user_id"]
        api_path = "api/rec/michaels/you_may_also_buy"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # api/rec/mktplace you_may_also_buy
        user_id = rec_db_instance["fgm_you_may_also_buy"].find_one()["user_id"]
        api_path = "api/rec/mktplace/you_may_also_buy"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_edu recommended_for_you
        user_id = rec_db_instance["b2b_edu_recommended_for_you"].find_one()["user_id"]
        api_path = "api/rec/b2b_edu/recommended_for_you"
        params = "?user_id=" + str(user_id)
        self._test_single_api(api_path, params)

        # b2b_edu seasonal_top_picks
        api_path = "api/rec/b2b_edu/seasonal_top_picks"
        self._test_single_api(api_path)

        # b2b_edu similar_items
        redis_key_list = list(rec_api_redis_client.hgetall("b2b_similar_items").keys())
        api_path = "api/rec/b2b_edu/similar_items"
        if len(redis_key_list) != 0:
            item_id = redis_key_list[0]
            params = "?item_id=" + item_id.decode("utf-8")
            self._test_single_api(api_path, params)
        else:
            self.err_msg = (
                f"{api_path} api error. Cannot get redis data from b2b_similar_items"
            )
            print(self.err_msg)

        # b2b_edu add_user_defined_trending_now
        category_path = "test_category"
        api_path = "api/rec/b2b_edu/add_user_defined_trending_now"
        sep = "%20"
        rec_item_ids = "111" + sep + "222" + sep + "333" + sep + "567"
        params = "?category_path=" + category_path + "&rec_item_ids=" + rec_item_ids
        self._test_single_api_put(api_path, params)

        # b2b_edu user_defined_trending_now
        category_path = rec_db_instance["b2b_edu_user_defined_trending_now"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/b2b_edu/user_defined_trending_now"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # michaels mik_popular_item_by_store
        store_id = rec_db_instance["mik_popular_item_by_store"].find_one()["store_id"]
        api_path = "api/rec/michaels/popular_item_by_store"
        params = "?store_id=" + str(store_id)
        self._test_single_api(api_path, params)

        # b2b_edu trending_now_model
        category_path = rec_db_instance["b2b_edu_trending_now"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/b2b_edu/trending_now_model"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # b2b_edu trending_now
        category_path = rec_db_instance["b2b_edu_user_defined_trending_now"].find_one()[
            "category_path"
        ]
        api_path = "api/rec/b2b_edu/trending_now"
        params = "?category_path=" + str(category_path)
        self._test_single_api(api_path, params)

        # b2b_edu trending_now_all_category
        api_path = "api/rec/b2b_edu/trending_now_all_category"
        params = (
            "?user_defined_trending_now="
            + "b2b_edu_user_defined_trending_now"
            + "&trending_now="
            + "b2b_edu_trending_now"
            + "&candidate_count="
            + str(5)
        )
        self._test_single_api(api_path, params)

        # b2b_edu search_people_also_buy
        items = rec_db_instance["b2b_edu_people_also_buy"].find()
        items_id = []
        count = 0
        for item in items:
            if count < 2:
                items_id.append(item["item_id"])
                count = count + 1
            else:
                break
        separator = "%20"
        items_id_list = separator.join(items_id)
        items_scores = "2" + separator + "3"
        api_path = "api/rec/b2b_edu/search_people_also_buy"
        params = "?items_id_list=" + items_id_list + "&items_scores=" + items_scores
        self._test_single_api(api_path, params)

        # b2b_edu search_rerank
        redis_key_list = list(rec_api_redis_client.hgetall("cbf_item_vector").keys())
        if len(redis_key_list) >= 4:
            field1 = redis_key_list[0].decode("utf-8")
            field2 = redis_key_list[1].decode("utf-8")
            field3 = redis_key_list[2].decode("utf-8")
            field4 = redis_key_list[3].decode("utf-8")
        separator = " "
        items_id_str = separator.join([field1, field2])
        order_history_str = separator.join([field3, field4])
        mimetype = "application/json"
        headers = {"Content-Type": mimetype, "Accept": mimetype}
        api_path = "api/rec/b2b_edu/search_rerank"
        data = {"items_id_list": items_id_str, "order_history_list": order_history_str}
        self._test_single_api_post(api_path, data=json.dumps(data), headers=headers)

        # store_name store_name_suggestion
        store_name = "johnson%20store"
        api_path = "store_name/store_name_suggestions"
        params = "?store_name=" + store_name
        token_response = requests.post(
            "https://usr.dev.platform.michaels.com/api/user/sign-in",
            json={
                "email": "dhmyydsstudio@gmail.com",
                "password": "Welcome20",
                "deviceUuid": "string",
                "deviceModel": "string",
                "deviceType": 0,
                "firebaseToken": "string",
                "deviceName": "string",
                "loginAddress": "string",
            },
        )
        if token_response.status_code == 200:
            token = token_response.json()["data"]["token"]
            try:
                result = requests.get(
                    f"{self.base_url}{api_path}{params}",
                    headers={"Authorization": token},
                )
                status_code = result.status_code
                if status_code != 200:
                    self.err_msg = f"{api_path} api error. Error code: {status_code}"
                    print(self.err_msg)
            except ConnectionError:
                self.err_msg = f"ERROR: {api_path} connection error"
                print(self.err_msg)
        else:
            self.err_msg = "Can not get token from mcu server"
            print(self.err_msg)

        # b2b_edu purchased_together_bundle
        purchased_together_items = rec_db_instance["b2b_edu_purchased_together"].find()
        items_id = []
        count = 0
        for item in purchased_together_items:
            if count < 2:
                items_id.append(item["item_id"])
                count = count + 1
            else:
                break
        separator = "%20"
        items_id_list = separator.join(items_id)
        api_path = "api/rec/b2b_edu/purchased_together_bundle"
        params = "?items_id_list=" + items_id_list
        self._test_single_api(api_path, params)

        # b2b_ent purchased_together_bundle
        purchased_together_items = rec_db_instance["b2b_ent_purchased_together"].find()
        items_id = []
        count = 0
        for item in purchased_together_items:
            if count < 2:
                items_id.append(item["item_id"])
                count = count + 1
            else:
                break
        separator = "%20"
        items_id_list = separator.join(items_id)
        api_path = "api/rec/b2b_ent/purchased_together_bundle"
        params = "?items_id_list=" + items_id_list
        self._test_single_api(api_path, params)

        # b2b_edu streaming_trending_now_list
        # api_path = "api/rec/b2b_edu/streaming_trending_now_list"
        # self._test_single_api(api_path)

        # b2b_ent streaming_trending_now_list
        # api_path = "api/rec/b2b_ent/streaming_trending_now_list"
        # self._test_single_api(api_path)

        # mik purchased_together_bundle
        purchased_together_items = rec_db_instance["mik_purchased_together"].find()
        items_id = []
        count = 0
        for item in purchased_together_items:
            if count < 2:
                items_id.append(item["item_id"])
                count = count + 1
            else:
                break
        separator = "%20"
        items_id_list = separator.join(items_id)
        api_path = "api/rec/michaels/purchased_together_bundle"
        params = "?items_id_list=" + items_id_list
        self._test_single_api(api_path, params)

        # fgm purchased_together_bundle
        purchased_together_items = rec_db_instance["fgm_purchased_together"].find()
        items_id = []
        count = 0
        for item in purchased_together_items:
            if count < 2:
                items_id.append(item["item_id"])
                count = count + 1
            else:
                break
        separator = "%20"
        items_id_list = separator.join(items_id)
        api_path = "api/rec/mktplace/purchased_together_bundle"
        params = "?items_id_list=" + items_id_list
        self._test_single_api(api_path, params)

        # MIK popular_products_in_projects
        api_path = "api/rec/michaels/popular_products_in_projects"
        self._test_single_api(api_path)

        # FGM popular_products_in_projects
        api_path = "api/rec/mktplace/popular_products_in_projects"
        self._test_single_api(api_path)

        # MIK popular_products_in_events
        api_path = "api/rec/michaels/popular_products_in_events"
        self._test_single_api(api_path)

        # FGM popular_products_in_events
        api_path = "api/rec/mktplace/popular_products_in_events"
        self._test_single_api(api_path)

        # FGM new_projects
        api_path = "api/rec/mktplace/new_projects"
        self._test_single_api(api_path)

        # MIK new_projects
        api_path = "api/rec/michaels/new_projects"
        self._test_single_api(api_path)

        # FGM upcoming_event
        api_path = "api/rec/mktplace/upcoming_event"
        params = "?event_type=" + "IN_STORE"
        self._test_single_api(api_path, params)

        # MIK upcoming_event
        api_path = "api/rec/michaels/upcoming_event"
        params = "?event_type=" + "IN_STORE"
        self._test_single_api(api_path, params)

        # MIK top_picks with redis user_id
        redis_key_list = list(
            rec_api_redis_client.hgetall("mik_streaming_top_picks").keys()
        )
        if len(redis_key_list) != 0:
            field = redis_key_list[0].decode("utf-8")
            api_path = "api/rec/michaels/top_picks"
            params = "?user_id=" + field
            self._test_single_api(api_path, params)
        else:
            self.err_msg = f"{api_path} api error. Cannot get redis data from mik_streaming_top_picks"
            print(self.err_msg)

        # FGM top_picks with redis user_id
        redis_key_list = list(
            rec_api_redis_client.hgetall("fgm_streaming_top_picks").keys()
        )
        if len(redis_key_list) != 0:
            field = redis_key_list[0].decode("utf-8")
            api_path = "api/rec/mktplace/top_picks"
            params = "?user_id=" + field
            self._test_single_api(api_path, params)
        else:
            self.err_msg = f"{api_path} api error. Cannot get redis data from fgm_streaming_top_picks"
            print(self.err_msg)

        # MIK top_picks with fake user_id
        user_id = "123"
        api_path = "api/rec/michaels/top_picks"
        params = "?user_id=" + user_id
        self._test_single_api(api_path, params)

        # FGM top_picks with fake user_id
        user_id = "123"
        api_path = "api/rec/mktplace/top_picks"
        params = "?user_id=" + user_id
        self._test_single_api(api_path, params)

        # CRM personalized_scores
        customer_email = crm_db_instance["personalized_scores"].find_one()[
            "customer_email"
        ]
        api_path = "api/rec/crm/personalized_scores"
        params = "?customer_email=" + customer_email
        self._test_single_api(api_path, params)

        # # MIK similar_ad_items
        # redis_key_list = list(
        #     rec_api_redis_client.hgetall("mik_similar_ad_items").keys()
        # )
        # api_path = "api/rec/michaels/similar_ad_items"
        # if len(redis_key_list) != 0:
        #     item_id = redis_key_list[0]
        #     params = "?item_id=" + item_id.decode("utf-8")
        #     self._test_single_api(api_path, params)
        # else:
        #     self.err_msg = (
        #         f"{api_path} api error. Cannot get redis data from mik_similar_ad_items"
        #     )
        #     print(self.err_msg)

        # ping
        api_path = "api/rec/ping"
        self._test_single_api(api_path)

        # healthcheck
        api_path = "api/rec/healthcheck"
        self._test_single_api(api_path)

        # word_embedding word_vectors
        words = "flower"
        api_path = "api/rec/word_embedding/word_vectors"
        params = "?words=" + words
        self._test_single_api(api_path, params)

        # word_embedding ngram_sentence_vector
        sentence = "I like reading comic_book"
        api_path = "api/rec/word_embedding/ngram_sentence_vector"
        params = "?sentence=" + sentence
        self._test_single_api(api_path, params)

        # word_embedding ngram_word_vectors
        words = "apple_pie"
        api_path = "api/rec/word_embedding/ngram_word_vectors"
        params = "?words=" + words
        self._test_single_api(api_path, params)

        # word_embedding phrase
        sentence = "this natural cotton sateen is environmentally friendly"
        api_path = "api/rec/word_embedding/phrase"
        params = "?sentence=" + sentence
        self._test_single_api(api_path, params)

        # word_embedding sentence_vector
        sentence = "How are you today"
        api_path = "api/rec/word_embedding/sentence_vector"
        params = "?sentence=" + sentence
        self._test_single_api(api_path, params)

        if self.err_msg == "":
            print("API Test Passed")
        else:
            print("API Test Failed")

    @test_run_time
    def _test_single_api_put(self, api_path: str, params: str = ""):
        return requests.put(f"{self.base_url}{api_path}{params}")

    @test_run_time
    def _test_single_api_post(
        self, api_path: str, params: str = "", data: dict = None, headers: dict = None
    ):
        return requests.post(
            f"{self.base_url}{api_path}{params}", data=data, headers=headers
        )

    @test_run_time
    def _test_single_api(self, api_path: str, params: str = ""):
        return requests.get(f"{self.base_url}{api_path}{params}")


if __name__ == "__main__":
    api_test(sys.argv[1]).run_test()
