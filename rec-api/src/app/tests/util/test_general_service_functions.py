import datetime
import json
import operator

import numpy as np
import pandas as pd
import pytest
import pickle

from app.main.util.general_service_functions import (
    search_people_also_buy,
    search_rerank,
    get_similar_items,
    get_trending_now_all_category,
    filter_recently_view_streaming_based_on_time,
    get_similar_ad_items,
    get_purchased_together_for_bundle,
    get_top_picks,
    general_picks_function,
    get_similar_items_for_bundle,
    get_shopping_cart_bundle,
    rank_similar_items_by_popularity_score,
    get_image_url_by_categories,
)
from app.main.util.test_connection import (
    create_connection,
    disconnection,
    create_local_connection,
    disconnect_local_connection,
)
from app.main.util.global_db_connection import redis_client
from app.main.util.global_vars import ad_items_status_redis_hkey
from app.main.model.michaels import ItemSimilarity

filter_args = pytest.filter_args
test_pab = pytest.test_pab


class TestGeneralServiceFunctions:
    @pytest.mark.parametrize(
        "mongo_filter_scored_item_with_collection_name",
        [test_pab],
        indirect=True,
    )
    def test_search_people_also_buy(
        self, mongo_filter_scored_item_with_collection_name
    ):
        expect = ["2", "1", "4"]
        results = search_people_also_buy(
            items_id_list="101 102",
            items_scores="10 5",
            candidate_count=10,
            collection_name="test_pab",
            **filter_args,
        )
        assert operator.eq(expect, results)

    def test_search_rerank(self):
        # The item vector in the redis is of size(1, 300) but here we are using size(1, 10) vector to test
        redis_client.hmset(
            "test_redis_hash_key",
            {
                "1011": pickle.dumps([1, 0, 0, 1, 0, 1, 1, 1, 0, 0]),
                "1022": pickle.dumps([1, 1, 1, 1, 0, 1, 0, 0, 1, 0]),
                "1033": pickle.dumps([0, 1, 0, 0, 1, 0, 0, 1, 1, 0]),
            },
        )
        expect = {"1011": 0.22360679774997896, "1022": 0.4082482904638631, "1055": -1}
        results = search_rerank(
            items_ids="1011 1022 1055",
            order_history="1033 1044",
            redis_hash_key="test_redis_hash_key",
            order_history_weights="1 2",
        )
        assert operator.eq(expect, results)

    def test_get_similar_ad_items(self):
        local_conn, local_col = create_local_connection()
        local_col.insert_many(
            [
                {"item_number": "item101_ad", "status": 1},
                {"item_number": "item111_ad", "status": 0},
                {"item_number": "item122_ad", "status": 1},
                {"item_number": "item133_ad", "status": 1},
            ]
        )
        # add fake ad items
        redis_client.hset(
            "similar_ad_items",
            "item1",
            json.dumps(
                {
                    "recommendations": [
                        "item101_ad",
                        "item111_ad",
                        "item122_ad",
                        "item133_ad",
                    ],
                    "score": [0.9, 0.8, 0.7, 0.6],
                }
            ),
        )
        # add fake ad items' status
        redis_client.hset(ad_items_status_redis_hkey, "item101_ad", "1".encode("utf-8"))
        redis_client.hset(ad_items_status_redis_hkey, "item122_ad", "0".encode("utf-8"))
        redis_client.hset(ad_items_status_redis_hkey, "item133_ad", "1".encode("utf-8"))

        result = get_similar_ad_items(
            item_id="item1",
            ad_candidate_count=2,
            redis_similar_ad_items_hash_key="similar_ad_items",
            similar_items_api=False,
            **filter_args,
        )
        disconnect_local_connection(local_conn)
        redis_client.delete(
            ad_items_status_redis_hkey,
            "similar_ad_items",
        )
        assert result[0]["skuNumber"] == "item101_ad"
        assert result[0]["adsId"]
        assert result[1]["skuNumber"] == "item133_ad"
        assert result[0]["adsId"]

    def test_get_similar_ad_items_not_found_in_redis(self):

        result = get_similar_ad_items(
            item_id="item1",
            ad_candidate_count=2,
            redis_similar_ad_items_hash_key="similar_ad_items",
            similar_items_api=False,
            **filter_args,
        )
        assert result == []

    def test_get_similar_ad_items_not_found_filtered_item(self):
        local_conn, local_col = create_local_connection()
        local_col.insert_many(
            [
                {"item_number": "item101_ad", "status": 0},
            ]
        )
        # add fake ad items
        redis_client.hset(
            "similar_ad_items",
            "item1",
            json.dumps(
                {
                    "recommendations": [
                        "item101_ad",
                    ],
                    "score": [0.9],
                }
            ),
        )

        result = get_similar_ad_items(
            item_id="item1",
            ad_candidate_count=2,
            redis_similar_ad_items_hash_key="similar_ad_items",
            similar_items_api=False,
            **filter_args,
        )
        redis_client.delete(
            ad_items_status_redis_hkey,
            "similar_ad_items",
        )
        disconnect_local_connection(local_conn)
        assert result == []

    def test_get_similar_items(self):
        # add fake non-ad items
        redis_similar_items_hkey = "similar_items"
        redis_client.hset(
            redis_similar_items_hkey,
            "item1",
            json.dumps(
                {
                    "recommendations": ["1", "2", "3", "4"],
                    "score": [0.9, 0.8, 0.7, 0.6],
                }
            ),
        )
        expect = ["1", "2"]
        result = get_similar_items(
            similar_items_model=ItemSimilarity,
            item_id="item1",
            candidate_count=2,
            redis_similar_items_hash_key=redis_similar_items_hkey,
            similar_items_api=True,
            **filter_args,
        )

        redis_client.delete(
            ad_items_status_redis_hkey,
            redis_similar_items_hkey,
        )
        assert operator.eq(expect, result)

    def test_get_similar_items_not_found_in_Redis(self):
        connection = create_connection()
        expect = []
        result = get_similar_items(
            similar_items_model=ItemSimilarity,
            item_id="item1",
            candidate_count=2,
            redis_similar_items_hash_key="similar_items",
            similar_items_api=True,
            **filter_args,
        )
        disconnection(connection)
        assert operator.eq(expect, result)

    def test_get_trending_now_all_category(self):
        local_conn, local_col = create_local_connection()
        local_col.insert_many(
            [
                {"item_number": "107", "status": 1},
                {"item_number": "115", "status": 0},
                {"item_number": "457", "status": 1},
                {"item_number": "110", "status": 1},
                {"item_number": "119", "status": 0},
                {"item_number": "786", "status": 1},
                {"item_number": "34", "status": 1},
                {"item_number": "56", "status": 1},
                {"item_number": "673", "status": 1},
                {"item_number": "12", "status": 1},
                {"item_number": "78", "status": 0},
                {"item_number": "235", "status": 1},
            ]
        )
        local_conn1, local_col1 = create_local_connection(collection_name="udf_tn_coll")
        local_conn2, local_col2 = create_local_connection(collection_name="tn_coll")
        local_col1.insert_many(
            [
                {
                    "category_path": "root//Shop Categories",
                    "recommendations": ["107", "115", "457"],
                },
                {
                    "category_path": "root//Brushes",
                    "recommendations": ["110", "119", "786"],
                },
            ]
        )
        local_col2.insert_many(
            [
                {
                    "category_path": "root//Brushes",
                    "recommendations": ["34", "56", "673"],
                },
                {
                    "category_path": "root//Paints",
                    "recommendations": ["12", "78", "235"],
                },
            ]
        )
        expect = [
            {
                "category_path": "root//Shop Categories",
                "recommendations": ["107", "457"],
            },
            {"category_path": "root//Brushes", "recommendations": ["110", "786"]},
            {"category_path": "root//Paints", "recommendations": ["12", "235"]},
        ]

        results = get_trending_now_all_category(
            trending_now="tn_coll",
            user_defined_trending_now="udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        assert operator.eq(expect, results)
        disconnect_local_connection(local_conn)
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)

    def test_filter_recently_view_streaming_based_on_time(self):
        local_conn, local_col = create_local_connection()
        local_col.insert_many(
            [
                {"item_number": "10567677", "status": 1},
                {"item_number": "10159989", "status": 1},
                {"item_number": "10597168", "status": 0},
            ]
        )
        now = datetime.date.today()
        data = {
            "view_list": ["10567677", "10159989", "10597168", "10339129"],
            "view_time": [
                (now - datetime.timedelta(days=3)).__format__("%Y-%m-%d")
                + "T17:41:45.919Z",
                (now - datetime.timedelta(days=5)).__format__("%Y-%m-%d")
                + "T17:41:43.304Z",
                (now - datetime.timedelta(days=6)).__format__("%Y-%m-%d")
                + "T16:58:27.602Z",
                (now - datetime.timedelta(days=20)).__format__("%Y-%m-%d")
                + "T16:58:15.932Z",
            ],
        }
        result = filter_recently_view_streaming_based_on_time(
            data=json.dumps(data),
            candidate_count=3,
            date_interval=7,
            **filter_args,
        )
        assert result == ["10567677", "10159989"]
        disconnect_local_connection(local_conn)

    def test_get_purchased_together_for_bundle_case_one(self):
        # Case 1:  Check if function returns value correctly
        local_conn1, local_col1 = create_local_connection(
            db_name="test", collection_name="mik_purchased_together"
        )
        local_col1.insert_many(
            [
                {
                    "item_id": "1001",
                    "recommendations": ["1", "2", "3"],
                    "score": [1, 2, 3],
                },
                {
                    "item_id": "1002",
                    "recommendations": ["1", "2", "3"],
                    "score": [1, 2, 3],
                },
                {
                    "item_id": "1003",
                    "recommendations": ["1", "2", "6"],
                    "score": [1, 2, 3],
                },
            ]
        )

        items_ids_list = ["1001", "1002", "1003"]
        collection_name = "mik_purchased_together"
        expect = ["2", "3", "1", "6"]

        result = get_purchased_together_for_bundle(items_ids_list, collection_name)
        disconnect_local_connection(local_conn1)
        assert operator.eq(expect, result)

    def test_get_purchased_together_for_bundle_case_two(self):
        # Case 2: to tests for na values in the dataframe
        local_conn1, local_col1 = create_local_connection(
            db_name="test", collection_name="mik_purchased_together"
        )
        local_col1.insert_many(
            [
                {
                    "item_id": "1001",
                    "recommendations": ["1", "2", "3"],
                    "score": [1, 2, 3],
                },
                {
                    "item_id": "1002",
                    "recommendations": [np.nan, "2", "3"],
                    "score": [np.nan, 2, 3],
                },
                {
                    "item_id": "1003",
                    "recommendations": ["4", "5", "6"],
                    "score": [1, 2, 3],
                },
            ]
        )

        items_ids_list = ["1001", "1002", "1003"]
        collection_name = "mik_purchased_together"
        expect = ["3", "2", "6", "5", "1", "4"]

        result = get_purchased_together_for_bundle(items_ids_list, collection_name)
        disconnect_local_connection(local_conn1)
        assert operator.eq(expect, result)

    def test_get_top_picks(self):
        local_conn, local_col = create_local_connection()
        local_col.insert_many(
            [
                {"item_number": "1023", "status": 1},
                {"item_number": "1045", "status": 0},
                {"item_number": "1067", "status": 1},
                {"item_number": "1098", "status": 1},
            ]
        )
        redis_client.hset(
            "redis_top_picks_hkey",
            "3759",
            json.dumps(
                {
                    "path_id_list": ["path1", "path2", "path3", "path4"],
                    "recommendations": ["1023", "1045", "1067", "1098"],
                    "view_time": [
                        "2021-05-25 10:54:16",
                        "2021-05-25 10:54:16",
                        "2021-05-25 10:54:16",
                        "2021-05-25 10:54:16",
                    ],
                }
            ),
        )
        expect = ["1023", "1067", "1098"]
        result = get_top_picks(
            popular_first_layer_category="popular_first_layer_category",
            user_id=3759,
            candidate_count=3,
            redis_hash_key="redis_top_picks_hkey",
            collection_name="popular_item_by_category",
            **filter_args,
        )
        assert operator.eq(expect, result)
        disconnect_local_connection(local_conn)

    def test_general_picks_function(self):
        local_conn, local_col = create_local_connection()
        local_col.insert_many(
            [
                {"item_number": "107", "status": 1},
                {"item_number": "115", "status": 0},
                {"item_number": "457", "status": 1},
                {"item_number": "110", "status": 1},
                {"item_number": "119", "status": 0},
                {"item_number": "786", "status": 1},
                {"item_number": "34", "status": 1},
                {"item_number": "56", "status": 1},
                {"item_number": "673", "status": 1},
                {"item_number": "12", "status": 1},
                {"item_number": "78", "status": 0},
                {"item_number": "235", "status": 1},
            ]
        )
        local_con1, local_col1 = create_local_connection(collection_name="gen_coll")
        local_col1.insert_many(
            [
                {
                    "category_path": "root//Shop Categories",
                    "recommendations": ["107", "115", "457"],
                },
                {
                    "category_path": "root//Brushes",
                    "recommendations": ["110", "119", "786"],
                },
                {
                    "category_path": "root//Frames",
                    "recommendations": ["34", "56", "673"],
                },
                {
                    "category_path": "root//Paints",
                    "recommendations": ["12", "78", "235"],
                },
            ]
        )
        category_list = [
            "root//Shop Categories",
            "root//Brushes",
            "root//Frames",
            "root//Paints",
        ]
        recommendations = [["107", "457"], ["110", "786"], ["34", "56"], ["12", "235"]]
        rec_rank = [0, 1, 2, 3]
        expect = pd.DataFrame(
            {
                "category_path": category_list,
                "recommendations": recommendations,
                "rec_rank": rec_rank,
            }
        )
        results = general_picks_function(
            category_list=category_list,
            collection_name="gen_coll",
            return_number=2,
            **filter_args,
        )
        disconnect_local_connection(local_conn)
        disconnect_local_connection(local_con1)
        assert results.equals(expect)

    def test_get_similar_items_for_bundle_function(self):
        redis_similar_items_hkey = "mik_similar_items"
        redis_client.hset(
            redis_similar_items_hkey,
            "1001",
            json.dumps(
                {
                    "recommendations": ["1", "2", "3"],
                    "score": [0.9, 0.8, 0.7],
                }
            ),
        )
        redis_client.hset(
            redis_similar_items_hkey,
            "1002",
            json.dumps(
                {
                    "recommendations": ["1", "5", "6"],
                    "score": [0.9, 0.8, 0.7],
                }
            ),
        )
        expect = ["1", "2", "5", "3", "6"]
        results = get_similar_items_for_bundle(
            ["1001", "1002"], redis_similar_items_hkey, "mik_similar_items"
        )
        redis_client.delete(redis_similar_items_hkey)
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "mongo_filter_scored_item_with_collection_name",
        ["fgm_purchased_together"],
        indirect=True,
    )
    def test_get_shopping_cart_bundle(
        self, mongo_filter_scored_item_with_collection_name
    ):
        expect = ["2", "1", "4"]
        results = get_shopping_cart_bundle(
            items_id_list="101 102",
            candidate_count=5,
            purchased_together_collection_name="fgm_purchased_together",
            similar_items_collection_name="fgm_similar_items",
            redis_similar_items_hash_key="fgm_similar_items",
            **filter_args,
        )
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "similar_items_list,expected",
        [
            (
                ["101", "201", "301", "401", "501", "601", "701"],
                ["101", "301", "201", "501", "701", "601", "401"],
            ),
            ([], []),
        ],
    )
    def test_rank_similar_items_by_popularity_score(self, similar_items_list, expected):
        collection_name = "popular_master_items"
        local_conn, local_col = create_local_connection(collection_name=collection_name)
        local_col.insert_many(
            [
                {"item_id": "301", "score": 6},
                {"item_id": "201", "score": 5},
                {"item_id": "501", "score": 5},
                {"item_id": "101", "score": 7},
                {"item_id": "601", "score": 1},
                {"item_id": "701", "score": 2},
            ]
        )

        results = rank_similar_items_by_popularity_score(
            similar_items_list=similar_items_list,
            collection_name=collection_name,
            **filter_args,
        )
        disconnect_local_connection(local_conn)
        assert operator.eq(expected, results)

    @pytest.mark.parametrize(
        "mongo_related_category",
        ["test_sch"],
        indirect=True,
    )
    def test_get_image_url_by_categories(self, mongo_related_category):
        expect = {"category1": "image1", "category2": "image2"}
        results = get_image_url_by_categories(
            category_list=[
                "root//shop//t1//t2//category1",
                "root//shop//t1//t2//category2",
                "root//shop//t1//t2//category3",
            ],
            candidate_count=2,
            collection_name="test_sch",
        )
        assert operator.eq(expect, results)


if __name__ == "__main__":
    pytest.main()
