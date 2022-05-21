import operator

import pytest
from mongoengine import DoesNotExist
import json
import time

from app.main.model.mktplace import (
    TrendingNowModel,
    UserDefTrendingNow,
    PopularEvent,
    PopularProject,
    PopularSearchKeyword,
    YouMayAlsoBuy,
    EventForYou,
    PopularProductsInProjects,
    YesterdayPopularItem,
    NewProjects,
    PopularFirstLayerCategory,
    FavoriteItem,
    ShopNearYou,
    UpcomingEvent,
    TrendingEvent,
    PopularVisitedEvents,
    PeopleAlsoBuy,
    PopularItemByStore,
    PopularVisitedProjects,
    PopularVisitedItems,
    ItemSimilarity,
    PopularProductsInEvents,
    ProjectSimilarity,
    RelatedCategoriesByCategory,
    SimilarEvents,
    RelatedQueriesByQuery,
    RelatedQueriesByCategory,
    RelatedCategoriesByQuery,
    FeaturedFirstLayerCategoryByUser,
    PopularItemByCategory,
)
from app.main.model.mktplace import PopularItem
from app.main.model.mktplace import UserRecommend
from app.main.model.mktplace import RecForYouSearch
from app.main.service.mktplace_service import (
    get_mktplace_recommended_for_you,
    # get_mktplace_recently_viewed,
    get_mktplace_search_people_also_buy,
    post_mktplace_search_rerank,
    get_mktplace_trending_now_model,
    get_mktplace_trending_now,
    get_mktplace_user_defined_trending_now,
    put_mktplace_user_defined_trending_now,
    get_mktplace_popular_event,
    get_mktplace_popular_project,
    get_mktplace_trending_now_all_category,
    get_mktplace_popular_search_keyword,
    get_mktplace_you_may_also_buy,
    get_mktplace_event_for_you,
    get_mktplace_purchased_together_bundle,
    get_mktplace_popular_products_in_projects,
    get_mktplace_yesterday_popular_item,
    get_mktplace_new_projects,
    get_mktplace_top_picks,
    get_mktplace_favorite_item,
    get_mktplace_upcoming_event,
    get_mktplace_shop_near_you,
    get_mktplace_trending_event,
    get_mktplace_popular_visited_events,
    get_mktplace_streaming_trending_now_list,
    get_mktplace_popular_first_layer_category,
    get_mktplace_people_also_buy,
    get_mktplace_popular_item_by_store,
    get_mktplace_popular_visited_projects,
    get_mktplace_popular_visited_items,
    get_mktplace_shopping_cart_bundle,
    get_mktplace_popular_products_in_events,
    get_mktplace_similar_projects,
    get_mktplace_related_categories_by_category,
    get_mktplace_similar_items_by_popularity,
    get_mktplace_similar_events,
    get_mktplace_related_queries_by_query,
    get_mktplace_related_queries_by_category,
    get_mktplace_related_categories_by_query,
    get_mktplace_picks_from_experts,
    get_mktplace_popular_item_by_category,
)
from app.main.service.mktplace_service import get_mktplace_similar_items
from app.main.service.mktplace_service import get_mktplace_popular_item
from app.main.service.mktplace_service import get_search_term_categories
from app.main.service.mktplace_service import get_mktplace_recently_viewed_streaming
from app.main.service.mktplace_service import get_mktplace_rec_for_you_search
from app.main.util.exception_handler import NotEnoughRecommendations
from app.main.util.test_connection import (
    create_local_connection,
    disconnect_local_connection,
)
from app.main.util.global_db_connection import redis_client
from app.main.util.controller_args import mktplace_args

# global var defined in conftest.py pytest_configure
filter_args = pytest.filter_args
test_pfe = pytest.test_pfe
test_tp = pytest.test_tp
project_filter_args = pytest.project_filter_args
recently_view_redis_data = pytest.recently_view_redis_data
test_pab = pytest.test_pab
search_rerank_data = pytest.search_rerank_data


class TestMktplaceService:
    @pytest.mark.parametrize(
        "item, expected",
        [
            ("item1", ["1", "2"]),
            ("item2", ["4"]),
            ("item3", []),
        ],
    )
    @pytest.mark.parametrize(
        "redis_similar_items",
        ["fgm_similar_items"],
        indirect=True,
    )
    def test_get_b2b_edu_similar_items_service(
        self, redis_similar_items, item, expected
    ):
        # Case 1: Get data from redis
        # Case 2: Get data from mongo
        # Case 3: data not exist
        similar_items = ItemSimilarity(
            item_id="item2",
            recommendations=["3", "4", "5"],
            score=[8, 7, 6],
        )
        similar_items.save()
        result = get_mktplace_similar_items(
            item_id=item,
            candidate_count=2,
            redis_similar_items_hash_key="fgm_similar_items",
            similar_items_api=True,
            **filter_args,
        )

        assert operator.eq(expected, result)

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            (321, ["2", "1"]),
            (111, ["7", "8", "9"]),
        ],
    )
    def test_get_mktplace_recommended_for_you_service_case_one_two(
        self, user_id, expected
    ):
        # Case 1: recommend_for_you object exists
        # Case 2: recommend_for_you object does not exist, popular_item object exists
        user_recommend = UserRecommend(
            user_id=321, recommendations=["3", "5", "2", "1"], score=[1, 5, 3, 6]
        )
        popular_item = PopularItem(group_id=0, recommendations=["7", "8", "9"])
        user_recommend.save()
        popular_item.save()
        results = get_mktplace_recommended_for_you(
            user_id=user_id, candidate_count=3, **filter_args
        )
        user_recommend.delete()
        popular_item.delete()
        assert operator.eq(expected, results)

    def test_get_mktplace_recommended_for_you_service_case_three(self):
        # Case 3: recommend_for_you object, popular_item object do not exist
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_recommended_for_you(
                user_id=543, candidate_count=3, **filter_args
            )
        assert str(excinfo.value) == "PopularItem matching query does not exist."

    def test_get_mktplace_popular_item_service(self):
        popular_item = PopularItem(
            group_id=0,
            recommendations=["1", "2", "3", "4"],
            score=[9, 4, 5, 7],
        )
        popular_item.save()
        expect = ["1", "2", "4"]
        results = get_mktplace_popular_item(candidate_count=3, **filter_args)
        popular_item.delete()
        assert operator.eq(expect, results)

    def test_get_search_term_categories(self):
        search_term = "paint"
        candidate_count = 1

        result = get_search_term_categories(
            search_term=search_term,
            candidate_count=candidate_count,
            word_vector_length=4,
        )
        expect = ["Party//Holiday Parties//Christmas Party"]
        assert operator.eq(expect, result)

    @pytest.mark.parametrize(
        "zip_code, expected",
        [
            ("75037", ["20394", "55785", "73585"]),
            ("56734", []),
        ],
    )
    def test_get_mktplace_shop_near_you_service(self, zip_code, expected):
        shop_near_you = ShopNearYou(
            zip_code=zip_code,
            recommendations=["20394", "55785", "73585"],
        )
        shop_near_you.save()
        expect = ["20394", "55785", "73585"]
        result = get_mktplace_shop_near_you(zip_code=zip_code, candidate_count=3)
        shop_near_you.delete()
        assert operator.eq(expect, result)

    @pytest.mark.parametrize(
        "items_id_list, items_scores ,expect",
        [
            ("101 102", "10 5", ["2", "1", "4"]),
            (
                "101 102",
                "10",
                "Length of items ids list and items scores list must match",
            ),
            ("101 102", None, ["2", "1", "4"]),
            ("106 107", None, ""),
        ],
    )
    @pytest.mark.parametrize(
        "mongo_filter_scored_item_with_collection_name",
        [test_pab],
        indirect=True,
    )
    def test_get_mktplace_search_people_also_buy_service(
        self,
        mongo_filter_scored_item_with_collection_name,
        items_id_list,
        items_scores,
        expect,
    ):
        # Case 1: item_id_list and score_list exist
        # Case 2: item_id_list and score_list have different length
        # Case 3: item_id_list exist, no score_list
        # Case 4: Data not exist
        try:
            results = get_mktplace_search_people_also_buy(
                items_id_list=items_id_list,
                items_scores=items_scores,
                candidate_count=10,
                collection_name=test_pab,
                **filter_args,
            )
        except Exception as excinfo:
            assert str(excinfo) == expect
        else:
            assert operator.eq(expect, results)

    def test_get_mktplace_top_picks_service_case_one(self):
        # Data exists in redis
        # add fake top picks items
        redis_top_picks_hkey = mktplace_args["top_picks_args"]["redis_hash_key"][
            "default"
        ]
        redis_client.hset(
            redis_top_picks_hkey,
            "3759",
            json.dumps(
                {
                    "path_id_list": ["path1", "path2", "path3", "path4"],
                    "recommendations": ["1", "2", "3", "4"],
                    "view_time": [
                        "2021-05-25 10:54:16",
                        "2021-05-25 10:54:16",
                        "2021-05-25 10:54:16",
                        "2021-05-25 10:54:16",
                    ],
                }
            ),
        )
        expect = ["1", "2", "4"]
        result = get_mktplace_top_picks(
            user_id="3759",
            candidate_count=3,
            redis_hash_key="fgm_streaming_top_picks",
            collection_name="fgm_popular_item_by_category",
            **filter_args,
        )
        redis_client.delete(redis_top_picks_hkey)
        assert operator.eq(expect, result)

    @pytest.mark.parametrize(
        "mongo_filter_inactive_category",
        [test_tp],
        indirect=True,
    )
    def test_get_mktplace_top_picks_service_case_two(
        self, mongo_filter_inactive_category
    ):
        # No data in redis
        popular_first_layer_category = PopularFirstLayerCategory(
            group_id=0,
            recommendations=["root//ABC", "root//DEF", "root//JKL"],
            score=[7, 5, 4],
        )
        popular_first_layer_category.save()
        expect = ["1", "2", "7"]
        result = get_mktplace_top_picks(
            user_id="5599",
            candidate_count=3,
            redis_hash_key="fgm_streaming_top_picks",
            collection_name=test_tp,
            **filter_args,
        )
        popular_first_layer_category.delete()
        assert operator.eq(expect, result)

    @pytest.mark.parametrize(
        "mongo_filter_inactive_category",
        [test_tp],
        indirect=True,
    )
    def test_get_mktplace_top_picks_service_case_three(
        self, mongo_filter_inactive_category
    ):
        # Not enough recommendations
        popular_first_layer_category = PopularFirstLayerCategory(
            group_id=0,
            recommendations=["root//AAA", "root//BBB", "root//CCC"],
            score=[7, 5, 4],
        )
        popular_first_layer_category.save()
        with pytest.raises(NotEnoughRecommendations) as excinfo:
            get_mktplace_top_picks(
                user_id="3569",
                candidate_count=3,
                redis_hash_key="fgm_streaming_top_picks",
                collection_name=test_tp,
                **filter_args,
            )
        popular_first_layer_category.delete()
        assert str(excinfo.value.detail) == "Not enough recommendations"

    def test_get_mktplace_top_picks_service_case_four(self):
        # no recommendations
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_top_picks(
                user_id="5678",
                candidate_count=3,
                redis_hash_key="fgm_streaming_top_picks",
                collection_name=test_tp,
                **filter_args,
            )
        assert (
            str(excinfo.value)
            == "PopularFirstLayerCategory matching query does not exist."
        )

    def test_get_mktplace_popular_search_keyword_service(self):
        popular_search_keywords = PopularSearchKeyword(
            group_id=0, recommendations=["Popular", "Search", "Terms"], score=[7, 6, 5]
        )
        popular_search_keywords.save()
        expect = ["Popular", "Search", "Terms"]
        results = get_mktplace_popular_search_keyword(candidate_count=3)
        popular_search_keywords.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_search_keyword_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_popular_search_keyword(candidate_count=3)
        assert (
            str(excinfo.value) == "PopularSearchKeyword matching query does not exist."
        )

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            (101, ["101", "102", "103"]),
            (23, ["13", "14", "15"]),
        ],
    )
    def test_get_mktplace_rec_for_you_search_service_case_one_two(
        self, user_id, expected
    ):
        # case 1: When User exists and case 2: user doesn't exists
        rec_for_you_search = RecForYouSearch(
            user_id=101, recommendations=["101", "102", "103"], score=[4, 5, 8]
        )
        popular_search_keywords = PopularSearchKeyword(
            group_id=0, recommendations=["13", "14", "15"], score=[7, 6, 5]
        )
        rec_for_you_search.save()
        popular_search_keywords.save()
        results = get_mktplace_rec_for_you_search(user_id=user_id, candidate_count=3)
        rec_for_you_search.delete()
        popular_search_keywords.delete()
        assert operator.eq(expected, results)

    def test_get_mktplace_rec_for_you_search_service_case_three(self):
        # If no search recommendations exist
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_rec_for_you_search(user_id=4, candidate_count=3)
        assert (
            str(excinfo.value) == "PopularSearchKeyword matching query does not exist."
        )

    @pytest.mark.parametrize(
        "request_data, expect",
        [
            (
                search_rerank_data[0],
                {"1022": 0.4082482904638631, "1011": 0.22360679774997896},
            ),
            (
                search_rerank_data[1],
                {"1011": 0.43968397092010375, "1022": 0.46941609682128776},
            ),
            (search_rerank_data[2], {"1011": 1, "1022": 1}),
            (
                search_rerank_data[4],
                "Length of order history list and items weights list must match",
            ),
            (search_rerank_data[5], "Item ID not found"),
            (search_rerank_data[3], "Item ID not found"),
        ],
    )
    def test_post_mktplace_search_rerank_service(
        self, redis_search_rerank, request_data, expect
    ):
        # The item vector in the redis is of size(1, 300) but here we are using size(1, 10) vector to test
        # Case 1: calculate similarity with 1 item in order history
        # Case 2: calculate similarity with 2 items in order history
        # Case 3: no order history in redis
        # Case 4: 500 error case
        # Case 5: item has no vector
        # Case 6: item not exist
        try:
            results = post_mktplace_search_rerank(json_dict=request_data)
        except Exception as excinfo:
            assert str(excinfo) == expect
        else:
            assert operator.eq(expect, results)

    def test_put_mktplace_user_defined_trending_now_service_case_one(self):
        # Case 1: Adding new category path and recommendations
        expect = {
            "category_path": "root//Frames",
            "recommendations": ["8786", "5435", "9034", "6789"],
        }
        result = put_mktplace_user_defined_trending_now(
            category_path="root//Frames", rec_item_ids="8786,5435,9034,6789"
        )

        # Compare new user defined trending now items that are inserted into DB with expected result
        user_def_tn_obj = UserDefTrendingNow.objects(category_path="root//Frames").get()
        user_def_tn_obj.save()
        user_def_tn_obj.delete()
        assert operator.eq(expect, result)
        assert operator.eq(expect["recommendations"], user_def_tn_obj.recommendations)

    def test_put_mktplace_user_defined_trending_now_service_case_two(self):
        # Case 2: Updating a category path with different recommendations
        local_conn, local_col = create_local_connection()
        local_col.insert_many(
            [
                {
                    "category_path": "root//Paints",
                    "recommendations": ["2525", "5561", "5658"],
                }
            ]
        )
        expect = {
            "category_path": "root//Paints",
            "recommendations": ["100", "200", "300", "500"],
        }
        result = put_mktplace_user_defined_trending_now(
            category_path="root//Paints", rec_item_ids="100,200,300,500"
        )

        # Compare new user defined trending now items that are updated into DB with expected result
        user_def_tn_obj = UserDefTrendingNow.objects(category_path="root//Paints").get()
        user_def_tn_obj.save()
        user_def_tn_obj.delete()
        disconnect_local_connection(local_conn)
        assert operator.eq(expect, result)
        assert operator.eq(expect["recommendations"], user_def_tn_obj.recommendations)

    def test_put_mktplace_user_defined_trending_now_service_case_three(self):
        # Case 3: Updating a category path with empty recommendations
        local_conn, local_col = create_local_connection()
        local_col.insert_many(
            [
                {
                    "category_path": "root//Canvas",
                    "recommendations": ["1578", "1236", "1780", "1997"],
                }
            ]
        )
        expect = {"category_path": "root//Canvas", "recommendations": []}
        result = put_mktplace_user_defined_trending_now(
            category_path="root//Canvas", rec_item_ids=""
        )

        user_def_tn_obj = UserDefTrendingNow.objects(category_path="root//Canvas").get()
        user_def_tn_obj.save()
        user_def_tn_obj.delete()
        disconnect_local_connection(local_conn)
        assert operator.eq(expect, result)
        assert operator.eq(expect["recommendations"], user_def_tn_obj.recommendations)

    @pytest.mark.parametrize(
        "category_path, recommendations, expected",
        [
            ("abc", ["1", "2", "3"], ["1", "2"]),
            ("def", [], []),
        ],
    )
    def test_get_mktplace_user_defined_trending_now_service_case_one_two(
        self, category_path, recommendations, expected
    ):
        # case 1: has category path and recommendations and case 2: has category path and no recommendations
        user_def_tn = UserDefTrendingNow(
            category_path=category_path, recommendations=recommendations
        )
        user_def_tn.save()
        results = get_mktplace_user_defined_trending_now(
            category_path=category_path,
            candidate_count=2,
            **filter_args,
        )
        user_def_tn.delete()
        assert operator.eq(expected, results)

    def test_get_mktplace_user_defined_trending_now_service_case_three(self):
        # Case 3: has no category path
        expect = []
        result = get_mktplace_user_defined_trending_now(
            category_path="sdf",
            candidate_count=2,
            **filter_args,
        )
        assert operator.eq(expect, result)

    @pytest.mark.parametrize(
        "category_path, recommendations, expected",
        [
            ("abc", ["5", "8", "9"], ["8", "9"]),
            ("def", [], []),
        ],
    )
    def test_get_mktplace_trending_now_model_service_case_one_two(
        self, category_path, recommendations, expected
    ):
        # case 1 : recommendations exist and case 2: recommendations doesn't exist
        trending_now = TrendingNowModel(
            category_path=category_path, recommendations=recommendations
        )
        trending_now.save()
        results = get_mktplace_trending_now_model(
            category_path=category_path,
            candidate_count=3,
            **filter_args,
        )
        trending_now.delete()
        assert operator.eq(expected, results)

    def test_get_mktplace_trending_now_model_service_case_three(self):
        # Case 3: has no category path
        expect = []
        result = get_mktplace_trending_now_model(
            category_path="aaa",
            candidate_count=2,
            **filter_args,
        )
        assert operator.eq(expect, result)

    def test_get_mktplace_trending_now_service_case_one(self):
        # Case 1: has user define category path and recommendations
        model_tn = TrendingNowModel(
            category_path="abc", recommendations=["4", "5", "6"]
        )
        user_tn = UserDefTrendingNow(
            category_path="abc", recommendations=["1", "2", "3"]
        )
        model_tn.save()
        user_tn.save()
        expect = ["1", "2"]
        results = get_mktplace_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        user_tn.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_trending_now_service_case_two(self):
        # Case 2: has user define category path but recommendations empty
        model_tn = TrendingNowModel(
            category_path="abc", recommendations=["1", "2", "3"]
        )
        user_tn = UserDefTrendingNow(category_path="abc", recommendations=[])
        model_tn.save()
        user_tn.save()
        expect = ["1", "2"]
        results = get_mktplace_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        user_tn.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_trending_now_service_case_three(self):
        # Case 3: has no user define category path but has model category path
        model_tn = TrendingNowModel(
            category_path="abc", recommendations=["1", "2", "3"]
        )
        model_tn.save()
        expect = ["1", "2"]
        results = get_mktplace_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_trending_now_service_case_four(self):
        # Case 4: has no user define category path and no model category path
        model_tn = TrendingNowModel(
            category_path="ghi", recommendations=["4", "6", "2"]
        )
        user_tn = UserDefTrendingNow(
            category_path="ghi", recommendations=["1", "3", "5"]
        )
        model_tn.save()
        user_tn.save()
        expect = []
        result = get_mktplace_trending_now(
            category_path="def",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        user_tn.delete()
        assert operator.eq(expect, result)

    def test_get_mktplace_trending_now_service_case_five(self):
        # Case 5: has no user define category path and model recommendation is empty
        model_tn = TrendingNowModel(category_path="abc", recommendations=[])
        model_tn.save()
        expect = []
        results = get_mktplace_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )

        model_tn.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_trending_now_all_category_service_case_one(self):
        # Case 1: has both user defined and trending now model
        local_conn1, local_col1 = create_local_connection(
            collection_name="fgm_udf_tn_coll"
        )
        local_conn2, local_col2 = create_local_connection(collection_name="fgm_tn_coll")
        local_col1.insert_many(
            [
                {
                    "category_path": "root//Shop Categories",
                    "recommendations": ["1", "2", "3"],
                },
                {
                    "category_path": "root//Brushes",
                    "recommendations": ["4", "5", "6"],
                },
            ]
        )
        local_col2.insert_many(
            [
                {
                    "category_path": "root//Brushes",
                    "recommendations": ["7", "8", "9"],
                },
                {
                    "category_path": "root//Paints",
                    "recommendations": ["3", "7", "8"],
                },
            ]
        )
        expect = [
            {
                "category_path": "root//Shop Categories",
                "recommendations": ["1", "2"],
            },
            {"category_path": "root//Brushes", "recommendations": ["4"]},
            {"category_path": "root//Paints", "recommendations": ["7", "8"]},
        ]

        results = get_mktplace_trending_now_all_category(
            trending_now="fgm_tn_coll",
            user_defined_trending_now="fgm_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, results)

    def test_get_mktplace_trending_now_all_category_service_case_two(self):
        # Case 2: has user defined but no trending now model
        local_conn1, local_col1 = create_local_connection(
            collection_name="fgm_udf_tn_coll"
        )
        local_conn2, local_col2 = create_local_connection(collection_name="fgm_tn_coll")
        local_col1.insert_many(
            [
                {
                    "category_path": "root//Shop Categories",
                    "recommendations": ["1", "2", "3"],
                },
                {
                    "category_path": "root//Brushes",
                    "recommendations": ["4", "5", "6"],
                },
            ]
        )
        expect = [
            {
                "category_path": "root//Shop Categories",
                "recommendations": ["1", "2"],
            },
            {"category_path": "root//Brushes", "recommendations": ["4"]},
        ]

        results = get_mktplace_trending_now_all_category(
            trending_now="fgm_tn_coll",
            user_defined_trending_now="fgm_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, results)

    def test_get_mktplace_trending_now_all_category_service_case_three(self):
        # Case 3: has trending now model but user defined model is empty
        local_conn1, local_col1 = create_local_connection(collection_name="fgm_tn_coll")
        local_conn2, local_col2 = create_local_connection(
            collection_name="fgm_udf_tn_coll"
        )
        local_col1.insert_many(
            [
                {
                    "category_path": "root//Shop Categories",
                    "recommendations": ["1", "2", "3"],
                },
                {
                    "category_path": "root//Brushes",
                    "recommendations": ["4", "5", "6"],
                },
            ]
        )
        expect = [
            {
                "category_path": "root//Shop Categories",
                "recommendations": ["1", "2"],
            },
            {"category_path": "root//Brushes", "recommendations": ["4"]},
        ]

        results = get_mktplace_trending_now_all_category(
            trending_now="fgm_tn_coll",
            user_defined_trending_now="fgm_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, results)

    def test_get_mktplace_trending_now_all_category_service_case_four(self):
        # Case 4: has no user defined model or trending now model
        expect = []
        results = get_mktplace_trending_now_all_category(
            trending_now="fgm_tn_coll",
            user_defined_trending_now="fgm_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        assert operator.eq(expect, results)

    def test_get_mktplace_event_for_you_service(
        self,
        mock_filter_no_schedule_events_in_mongo,
        mock_filter_archived_events_in_mongo,
    ):
        event_recommend = EventForYou(
            user_id=765, recommendations=["1", "2", "3"], score=[1, 4, 7]
        )
        event_recommend.save()
        expect = ["1", "2", "3"]
        results = get_mktplace_event_for_you(
            user_id=765,
            candidate_count=3,
            spanner_table_name="test_events",
            event_type="IN_STORE",
        )
        event_recommend.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_event_for_you_service_404(
        self,
        mock_filter_no_schedule_events_in_mongo,
        mock_filter_archived_events_in_mongo,
    ):
        event_recommend = EventForYou(
            user_id=822, recommendations=["32", "22", "12"], score=[1, 4, 7]
        )
        popular_event = PopularEvent(
            group_id=0, recommendations=["1", "2", "3"], score=[1, 2]
        )
        event_recommend.save()
        popular_event.save()
        expect = ["1", "2", "3"]
        results = get_mktplace_event_for_you(
            user_id=111,
            candidate_count=2,
            spanner_table_name="test_events",
            event_type="IN_STORE",
        )
        popular_event.delete()
        event_recommend.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_event_service(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        popular_event = PopularEvent(
            group_id=0, recommendations=["1", "2", "3"], score=[11, 33, 54]
        )
        popular_event.save()
        expect = ["1", "2", "3"]
        results = get_mktplace_popular_event(candidate_count=3, event_type="IN_STORE")
        popular_event.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_project_service(self):
        popular_project = PopularProject(
            group_id=0, recommendations=["1", "2", "3"], score=[4, 7, 10]
        )
        popular_project.save()
        expect = ["1", "2"]
        results = get_mktplace_popular_project(candidate_count=2, **project_filter_args)
        popular_project.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_project_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_popular_project(
                candidate_count=2,
                **project_filter_args,
            )
        assert str(excinfo.value) == "PopularProject matching query does not exist."

    @pytest.mark.parametrize(
        "mock_redis_client",
        [recently_view_redis_data],
        indirect=True,
    )
    def test_mktplace_recently_viewed_streaming(self, mock_redis_client):
        rec_api_redis_client = mock_redis_client
        expect = ["1", "2"]
        result = get_mktplace_recently_viewed_streaming(
            user_id="123456",
            candidate_count=4,
            date_interval=10,
            **filter_args,
        )
        assert result == expect

    @pytest.mark.parametrize(
        "mock_redis_client",
        [None],
        indirect=True,
    )
    def test_mktplace_recently_viewed_streaming_404(self, mock_redis_client):
        rec_api_redis_client = mock_redis_client
        response = get_mktplace_recently_viewed_streaming(
            user_id="123456",
            candidate_count=4,
            date_interval=7,
            **filter_args,
        )
        assert response == []

    # @mock.patch("app.main.service.mktplace_service.bigquery_client", autospec=True)
    # def test_get_mktplace_recently_viewed_service(
    #     self, mock_bigquery_client
    # ):
    #     data = pd.DataFrame([[13, 20], [13, 16]], columns=["user_id", "item_id"])
    #     mock_bigquery_client.query.return_value.result.return_value.to_dataframe.return_value = (
    #         data
    #     )
    #     local_conn, local_col = create_local_connection()
    #     local_col.insert_many(
    #         [
    #             {"item_number": 20, "status": 1},
    #             {"item_number": 16, "status": 1},
    #         ]
    #     )
    #     result = get_mktplace_recently_viewed(
    #         user_id="13", candidate_count=4, **filter_args
    #     )
    #     assert result == [20, 16]
    #     disconnect_local_connection(local_conn)
    #
    # @mock.patch("app.main.service.mktplace_service.bigquery_client", autospec=True)
    # def test_get_mktplace_recently_viewed_service_404(self, mock_bigquery_client):
    #     data = pd.DataFrame([], columns=["user_id", "item_id"])
    #     mock_bigquery_client.query.return_value.result.return_value.to_dataframe.return_value = (
    #         data
    #     )
    #     try:
    #         get_mktplace_recently_viewed(
    #             user_id="13",
    #             candidate_count=4,
    #             **filter_args,
    #         )
    #     except DoesNotExist:
    #         assert True

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            ("777", ["1", "2"]),
            ("99", ["7", "8"]),
        ],
    )
    def test_get_mktplace_you_may_also_buy_service(self, user_id, expected):
        # Case 1: With user id
        # Case 2: Without user id
        you_may_also_buy = YouMayAlsoBuy(user_id="777", recommendations=["1", "2", "3"])
        popular_item = PopularItem(
            group_id=0, recommendations=["6", "7", "8"], score=[7, 6, 5]
        )
        you_may_also_buy.save()
        popular_item.save()
        results = get_mktplace_you_may_also_buy(
            user_id=user_id, candidate_count=2, **filter_args
        )
        you_may_also_buy.delete()
        popular_item.delete()
        assert operator.eq(expected, results)

    @pytest.mark.parametrize(
        "items_id_list, expected",
        [
            ("1001 1002 1003", ["2", "1"]),
            ("1004", []),
        ],
    )
    def test_get_mktplace_purchased_together_bundle_service_case_one_two(
        self, mongo_insert_items_list, items_id_list, expected
    ):
        # Case 1: With valid item_id_list
        # Case 2: Without valid item_list
        result = get_mktplace_purchased_together_bundle(
            items_id_list=items_id_list,
            candidate_count=3,
            collection_name="test_collection",
            **filter_args,
        )
        assert operator.eq(expected, result)

    def test_get_mktplace_popular_products_in_projects_service(self):
        popular_products_in_projects = PopularProductsInProjects(
            group_id=0, recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        popular_products_in_projects.save()
        expect = ["1", "2"]
        results = get_mktplace_popular_products_in_projects(
            candidate_count=2, **filter_args
        )
        popular_products_in_projects.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_products_in_projects_empty(self):
        popular_products_in_projects = PopularProductsInProjects(
            group_id=0, recommendations=[], score=[]
        )
        popular_products_in_projects.save()
        results = get_mktplace_popular_products_in_projects(
            candidate_count=3, **filter_args
        )
        popular_products_in_projects.delete()
        assert operator.eq(results, [])

    def test_get_mktplace_yesterday_popular_item_service(self):
        yesterday_popular_item = YesterdayPopularItem(
            group_id=0, recommendations=["2", "4", "6", "8"], score=[4, 6, 7, 1]
        )
        yesterday_popular_item.save()
        expect = ["2", "4", "8"]
        results = get_mktplace_yesterday_popular_item(candidate_count=3, **filter_args)
        yesterday_popular_item.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_yesterday_popular_item_service_404(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_yesterday_popular_item(candidate_count=2, **filter_args)
        assert (
            str(excinfo.value) == "YesterdayPopularItem matching query does not exist."
        )

    @pytest.mark.parametrize(
        "reccomendations, expected",
        [
            (["1", "2", "3"], ["1", "2"]),
            ([], []),
        ],
    )
    def test_get_mktplace_new_projects_service(self, reccomendations, expected):
        new_projects = NewProjects(group_id=0, recommendations=reccomendations)
        new_projects.save()

        results = get_mktplace_new_projects(candidate_count=2, **project_filter_args)
        new_projects.delete()
        assert operator.eq(expected, results)

    def test_get_mktplace_favorite_item_service(self):
        favorite_item = FavoriteItem(
            group_id=0, recommendations=["1", "2", "3", "4"], score=[4, 6, 7, 1]
        )
        favorite_item.save()
        expect = ["1", "2", "4"]
        results = get_mktplace_favorite_item(candidate_count=3, **filter_args)
        favorite_item.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_favorite_item_service_404(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_favorite_item(candidate_count=2, **filter_args)
        assert str(excinfo.value) == "FavoriteItem matching query does not exist."

    def test_get_mktplace_upcoming_event_service(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        test_timestamp = int(time.time()) % (24 * 3600) // 900 * 900
        upcoming_event = UpcomingEvent(
            timestamp=test_timestamp,
            events_id=["1", "2", "3"],
            schedules_id=[11, 22, 33],
        )
        upcoming_event.save()

        expect = [{"event_id": ["1", "2", "3"], "schedules_id": [11, 22, 33]}]
        results = get_mktplace_upcoming_event(candidate_count=3, event_type="ONLINE")
        upcoming_event.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_upcoming_event_service_failed(self):
        try:
            get_mktplace_upcoming_event(candidate_count=2, event_type="IN_STORE")
        except DoesNotExist:
            assert True

    def test_get_mktplace_trending_event_service(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        trending_event = TrendingEvent(
            group_id=0, recommendations=["1", "2", "3"], score=[11, 33, 54]
        )
        trending_event.save()
        expect = ["1", "2", "3"]
        results = get_mktplace_trending_event(candidate_count=3, event_type="IN_STORE")
        trending_event.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_trending_event_service_404(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_trending_event(candidate_count=2, event_type="IN_STORE")
        assert str(excinfo.value) == "TrendingEvent matching query does not exist."

    def test_get_mktplace_popular_item_by_store_service(self):
        popular_item_by_store = PopularItemByStore(
            store_id=285, recommendations=["1", "2", "3"], score=[8, 7, 6]
        )
        popular_item_by_store.save()
        expect = ["1", "2"]
        results = get_mktplace_popular_item_by_store(
            store_id=285,
            candidate_count=2,
            **filter_args,
        )
        popular_item_by_store.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_item_by_store_failed(self):
        popular_item_by_store = PopularItemByStore(
            store_id=534, recommendations=["56", "78", "69"], score=[8, 7, 6]
        )

        popular_item_by_store.save()
        result = get_mktplace_popular_item_by_store(
            store_id=37,
            candidate_count=2,
            **filter_args,
        )
        popular_item_by_store.delete()
        assert result == []

    def test_get_mktplace_popular_visited_events_service(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        popular_visited_events = PopularVisitedEvents(
            group_id=0, recommendations=["1001", "1002", "1003"], score=[18, 15, 13]
        )
        popular_visited_events.save()
        expect = ["1", "2", "3"]
        results = get_mktplace_popular_visited_events(
            candidate_count=2, event_type="IN_STORE"
        )
        popular_visited_events.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_visited_events_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_popular_visited_events(
                candidate_count=2,
                spanner_table_name="test_events",
                event_type="IN_STORE",
            )
        assert (
            str(excinfo.value) == "PopularVisitedEvents matching query does not exist."
        )

    # def test_get_mktplace_streaming_trending_now_list_service(self):
    #     redis_streaming_trending_now_list_key = mktplace_args[
    #         "streaming_trending_now_list_args"
    #     ]["redis_streaming_trending_now_list_key"]["default"]
    #     redis_client.set(
    #         redis_streaming_trending_now_list_key,
    #         json.dumps({"item_list": ["item101", "item102", "item103"]}),
    #     )
    #     local_conn, local_col = create_local_connection()
    #     connection = create_connection()
    #     local_col.insert_many(
    #         [
    #             {"item_number": "item101", "status": 1},
    #             {"item_number": "item102", "status": 0},
    #             {"item_number": "item103", "status": 1},
    #             {"item_number": "item104", "status": 1},
    #         ]
    #     )
    #
    #     expect = ["item101", "item103"]
    #     results = get_mktplace_streaming_trending_now_list(
    #         candidate_count=2,
    #         redis_streaming_trending_now_list_key="fgm_streaming_trending_now_list",
    #         **filter_args,
    #     )
    #     redis_client.delete(redis_streaming_trending_now_list_key)
    #     disconnect_local_connection(local_conn)
    #     disconnection(connection)
    #     assert operator.eq(expect, results)
    #
    # def test_get_mktplace_streaming_trending_now_list_service_404(self):
    #     try:
    #         get_mktplace_streaming_trending_now_list(
    #             candidate_count=2,
    #             redis_streaming_trending_now_list_key="fgm_streaming_trending_now_list",
    #             **filter_args,
    #         )
    #     except NotFound:
    #         assert True

    def test_get_mktplace_popular_first_layer_category_service(self):
        popular_first_layer_category = PopularFirstLayerCategory(
            group_id=0, recommendations=["A", "B", "C"], score=[18, 15, 13]
        )
        popular_first_layer_category.save()
        expect = ["A", "B"]
        results = get_mktplace_popular_first_layer_category(candidate_count=2)
        popular_first_layer_category.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_first_layer_category_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_popular_first_layer_category(candidate_count=2)
        assert (
            str(excinfo.value)
            == "PopularFirstLayerCategory matching query does not exist."
        )

    def test_get_mktplace_people_also_buy_service(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="777", recommendations=["8", "7", "6"], score=[3, 5, 8]
        )
        people_also_buy.save()
        expect = ["8", "7"]
        results = get_mktplace_people_also_buy(
            item_id="777", candidate_count=2, **filter_args
        )
        people_also_buy.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_people_also_buy_service_failed(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="999", recommendations=["14", "15", "16"], score=[1, 2, 9]
        )
        people_also_buy.save()
        expect = []
        results = get_mktplace_people_also_buy(
            item_id="99",
            candidate_count=2,
            **filter_args,
        )
        people_also_buy.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_visited_projects_service(self):
        popular_visited_projects = PopularVisitedProjects(
            group_id=0, recommendations=["1", "2", "3"], score=[18, 15, 13]
        )
        popular_visited_projects.save()
        expect = ["1", "2"]
        results = get_mktplace_popular_visited_projects(candidate_count=2)
        popular_visited_projects.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_visited_projects_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_popular_visited_projects(candidate_count=2)
        assert (
            str(excinfo.value)
            == "PopularVisitedProjects matching query does not exist."
        )

    def test_get_mktplace_popular_visited_items_service(self):
        popular_visited_items = PopularVisitedItems(
            group_id=0, recommendations=["1", "2", "3"], score=[18, 15, 13]
        )
        popular_visited_items.save()
        expect = ["1", "2"]
        results = get_mktplace_popular_visited_items(candidate_count=2)
        popular_visited_items.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_visited_items_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_popular_visited_items(candidate_count=2)
        assert (
            str(excinfo.value) == "PopularVisitedItems matching query does not exist."
        )

    @pytest.mark.parametrize(
        "items_id_list, expect",
        [
            ("101 102", ["2", "1", "4"]),
            ("106 107", ["1", "2", "4"]),
            ("103 104 105", ["2", "1", "7"]),
            ("108 109", []),
        ],
    )
    @pytest.mark.parametrize(
        "mongo_filter_scored_item_with_collection_name",
        ["fgm_purchased_together"],
        indirect=True,
    )
    def test_get_mktplace_shopping_cart_bundle_service(
        self, mongo_filter_scored_item_with_collection_name, items_id_list, expect
    ):
        # Case 1: get recommendations from purchased_together
        # Case 2: get recommendations from similar_items
        # Case 3: get recommendations from purchased_together and similar_items, remove duplicated recommendations
        # Case 4: get [] for data not found
        redis_similar_items_hkey = mktplace_args["similar_items_args"][
            "redis_similar_items_hash_key"
        ]["default"]
        redis_client.hset(
            redis_similar_items_hkey,
            "103",
            json.dumps(
                {
                    "recommendations": ["1", "2", "3"],
                    "score": [0.9, 0.8, 0.7],
                }
            ),
        )
        redis_client.hset(
            redis_similar_items_hkey,
            "104",
            json.dumps(
                {
                    "recommendations": ["1", "7", "3"],
                    "score": [0.9, 0.8, 0.7],
                }
            ),
        )
        redis_client.hset(
            redis_similar_items_hkey,
            "106",
            json.dumps(
                {
                    "recommendations": ["1", "2", "3"],
                    "score": [0.9, 0.8, 0.7],
                }
            ),
        )
        redis_client.hset(
            redis_similar_items_hkey,
            "107",
            json.dumps(
                {
                    "recommendations": ["1", "4", "3"],
                    "score": [0.9, 0.8, 0.7],
                }
            ),
        )
        results = get_mktplace_shopping_cart_bundle(
            items_id_list=items_id_list,
            candidate_count=5,
            purchased_together_collection_name="fgm_purchased_together",
            similar_items_collection_name="fgm_similar_items",
            redis_similar_items_hash_key="fgm_similar_items",
            **filter_args,
        )
        redis_client.delete(redis_similar_items_hkey)
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "mongo_filter_scored_item_with_collection_name",
        ["fgm_similar_items"],
        indirect=True,
    )
    def test_get_mktplace_shopping_cart_bundle_service_case_five(
        self, mongo_filter_scored_item_with_collection_name
    ):
        # Case 5: get recommendations from collection similar_items
        expect = ["2", "1"]
        results = get_mktplace_shopping_cart_bundle(
            items_id_list="103 104",
            candidate_count=5,
            purchased_together_collection_name="fgm_purchased_together",
            similar_items_collection_name="fgm_similar_items",
            redis_similar_items_hash_key="fgm_similar_items",
            **filter_args,
        )
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "recommendations, scores, expect",
        [
            (["1", "2", "3"], [7, 6, 5], ["1", "2"]),
            ([], [], []),
        ],
    )
    def test_get_mktplace_popular_products_in_events_service(
        self, recommendations, scores, expect
    ):
        popular_products_in_events = PopularProductsInEvents(
            group_id=0, recommendations=recommendations, score=scores
        )

        popular_products_in_events.save()
        results = get_mktplace_popular_products_in_events(
            candidate_count=2, **filter_args
        )
        popular_products_in_events.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_popular_products_in_events_404(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_popular_products_in_events(candidate_count=5, **filter_args)
        assert (
            str(excinfo.value)
            == "PopularProductsInEvents matching query does not exist."
        )

    def test_get_mktplace_similar_projects_service(self):
        project_similarity = ProjectSimilarity(
            external_id="1003", recommendations=["1", "2", "3"], score=[1, 2, 8]
        )
        project_similarity.save()
        expect = ["1", "2"]
        results = get_mktplace_similar_projects(
            candidate_count=2, external_id="1003", **project_filter_args
        )
        project_similarity.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_similar_projects_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_similar_projects(
                candidate_count=3, external_id="1005", **project_filter_args
            )
        assert str(excinfo.value) == "ProjectSimilarity matching query does not exist."

    def test_get_mktplace_similar_events_service(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        event_similarity = SimilarEvents(
            event_id="12003", recommendations=["1", "2", "3"], score=[2, 6, 8]
        )
        event_similarity.save()
        expect = ["1", "2", "3"]
        results = get_mktplace_similar_events(
            candidate_count=3,
            event_id="12003",
            event_type="ONLINE",
        )
        event_similarity.delete()
        assert operator.eq(expect, results)

    def test_get_mktplace_similar_events_service_failed(self):
        event_similarity = SimilarEvents(
            event_id="51004", recommendations=["4045", "5055", "6065"], score=[2, 6, 8]
        )
        event_similarity.save()
        with pytest.raises(DoesNotExist) as excinfo:
            get_mktplace_similar_events(
                candidate_count=3,
                event_id="51005",
                event_type="ONLINE",
            )
        event_similarity.delete()
        assert str(excinfo.value) == "SimilarEvents matching query does not exist."

    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("category_input", ["category1", "category2"]),
            ("invalid_category_input", []),
        ],
    )
    def test_get_mktplace_related_categories_by_category_service(
        self, category_path, expected
    ):
        related_categories_by_category = RelatedCategoriesByCategory(
            category_path="category_input",
            recommendations=["category1", "category2", "category3"],
        )
        related_categories_by_category.save()
        result = get_mktplace_related_categories_by_category(
            category_path=category_path,
            candidate_count=2,
        )
        related_categories_by_category.delete()
        assert operator.eq(expected, result)

    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("abc", ["1", "2"]),
            ("def", []),
        ],
    )
    def test_get_mktplace_popular_item_by_category_service(
        self, category_path, expected
    ):
        # Case 1: With popular item by category data
        # Case 2: Without popular item by category data
        popular_item_by_category = PopularItemByCategory(
            category_path="abc", recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        popular_item_by_category.save()
        result = get_mktplace_popular_item_by_category(
            category_path=category_path, candidate_count=2, **filter_args
        )
        popular_item_by_category.delete()
        assert operator.eq(expected, result)

    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("category_input", ["query1", "query2"]),
            ("invalid_category_input", []),
        ],
    )
    def test_get_mktplace_related_queries_by_category_service(
        self, category_path, expected
    ):
        related_queries_by_category = RelatedQueriesByCategory(
            category_path="category_input",
            recommendations=["query1", "query2", "query3"],
        )
        related_queries_by_category.save()
        result = get_mktplace_related_queries_by_category(
            category_path=category_path,
            candidate_count=2,
        )
        related_queries_by_category.delete()
        assert operator.eq(expected, result)

    @pytest.mark.parametrize(
        "input_item_id,expected",
        [
            (
                "item1",
                ["4", "1", "2"],
            ),
            ("item_id_not_found", []),
        ],
    )
    @pytest.mark.parametrize(
        "mongo_similar_items_by_popularity",
        ["fgm_popular_master_items"],
        indirect=True,
    )
    def test_get_mktplace_similar_items_by_popularity_service(
        self, input_item_id, expected, mongo_similar_items_by_popularity
    ):
        collection_name = "fgm_popular_master_items"
        redis_similar_items_hkey = mktplace_args["similar_items_args"][
            "redis_similar_items_hash_key"
        ]["default"]
        redis_client.hset(
            redis_similar_items_hkey,
            "item1",
            json.dumps(
                {
                    "recommendations": ["1", "2", "3", "4", "5", "6"],
                    "score": [0.9, 0.8, 0.7, 0.6, 0.5, 0.4],
                }
            ),
        )
        results = get_mktplace_similar_items_by_popularity(
            item_id=input_item_id,
            collection_name=collection_name,
            candidate_count=5,
            redis_similar_items_hash_key="fgm_similar_items",
            **filter_args,
        )
        redis_client.delete(redis_similar_items_hkey)
        assert operator.eq(expected, results)

    @pytest.mark.parametrize(
        "query_keyword, expected",
        [("query_input", ["1", "2", "3"]), ("invalid_query_input", [])],
    )
    def test_get_mktplace_related_queries_by_query_service(
        self, query_keyword, expected
    ):
        related_queries = RelatedQueriesByQuery(
            query="query_input", recommendations=["1", "2", "3"], score=[7, 6, 5]
        )

        related_queries.save()
        results = get_mktplace_related_queries_by_query(
            candidate_count=3,
            query_keyword=query_keyword,
        )
        related_queries.delete()
        assert operator.eq(expected, results)

    @pytest.mark.parametrize(
        "query_keyword, expected",
        [
            ("query_keyword", ["category1", "category2"]),
            ("invalid_query_keyword", []),
        ],
    )
    def test_get_mktplace_related_categories_by_query_service(
        self, query_keyword, expected
    ):
        related_categories_by_query = RelatedCategoriesByQuery(
            query="query_keyword",
            recommendations=["category1", "category2", "category3"],
            score=[1, 2, 3],
        )
        related_categories_by_query.save()
        result = get_mktplace_related_categories_by_query(
            query_keyword=query_keyword,
            candidate_count=2,
        )
        related_categories_by_query.delete()
        assert operator.eq(expected, result)

    @pytest.mark.parametrize(
        "mongo_filter_inactive_item_with_collection_name, mongo_filter_inactive_category",
        [(test_pfe, test_pfe)],
        indirect=True,
    )
    class TestGetMktplacePicksFromExpectsService:
        def test_get_mktplace_picks_from_experts_case_one(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            # Both featured_first_layer and popular_first_layer exist
            featured_first_layer_category = FeaturedFirstLayerCategoryByUser(
                user_id=16,
                recommendations=["root//ABC", "root//DEF", "root//GHI"],
                score=[3, 2, 1],
            )
            popular_first_layer_category = PopularFirstLayerCategory(
                group_id=0,
                recommendations=["root//AAA", "root//BBB", "root//CCC"],
                score=[7, 5, 4],
            )

            popular_first_layer_category.save()
            featured_first_layer_category.save()
            expect = {"root//ABC": ["1", "4"], "root//DEF": ["2", "7"]}
            result = get_mktplace_picks_from_experts(
                user_id=16,
                category_count=2,
                category_buffer=2,
                candidate_count=2,
                collection_name=test_pfe,
                **filter_args,
            )

            featured_first_layer_category.delete()
            popular_first_layer_category.delete()
            assert operator.eq(expect, result)

        def test_get_mktplace_picks_from_experts_case_two(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            # Only popular_first_layer exists
            popular_first_layer_category = PopularFirstLayerCategory(
                group_id=0,
                recommendations=["root//ABC", "root//DEF", "root//GHI"],
                score=[7, 5, 4],
            )

            popular_first_layer_category.save()
            expect = {"root//ABC": ["1", "4"], "root//DEF": ["2", "7"]}
            result = get_mktplace_picks_from_experts(
                user_id=0,
                category_count=2,
                category_buffer=2,
                candidate_count=2,
                collection_name=test_pfe,
                **filter_args,
            )
            popular_first_layer_category.delete()
            assert operator.eq(expect, result)

        def test_get_mktplace_picks_from_experts_case_three(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            # Only featured_first_layer exists
            featured_first_layer_category = FeaturedFirstLayerCategoryByUser(
                user_id=11,
                recommendations=["root//ABC", "root//DEF"],
                score=[3, 2],
            )
            featured_first_layer_category.save()

            expect = {"root//ABC": ["1", "4"], "root//DEF": ["2", "7"]}
            result = get_mktplace_picks_from_experts(
                user_id=11,
                category_count=2,
                category_buffer=2,
                candidate_count=2,
                collection_name=test_pfe,
                **filter_args,
            )
            featured_first_layer_category.delete()
            assert operator.eq(expect, result)

        def test_get_mktplace_picks_from_experts_case_four(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            # Categories with no recommended items
            featured_first_layer_category = FeaturedFirstLayerCategoryByUser(
                user_id=11,
                recommendations=["root//HGI", "root//JKL"],
                score=[3, 2],
            )
            featured_first_layer_category.save()
            with pytest.raises(NotEnoughRecommendations) as excinfo:
                get_mktplace_picks_from_experts(
                    user_id=11,
                    category_count=2,
                    category_buffer=2,
                    candidate_count=2,
                    collection_name=test_pfe,
                    **filter_args,
                )
            featured_first_layer_category.delete()
            assert str(excinfo.value.detail) == "Not enough recommendations"

        def test_get_mktplace_picks_from_experts_case_five(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            # Categories with no active item recommendations in some categories
            featured_first_layer_category = FeaturedFirstLayerCategoryByUser(
                user_id=11,
                recommendations=["root//ABC", "root//GHI"],
                score=[3, 2],
            )

            featured_first_layer_category.save()
            with pytest.raises(NotEnoughRecommendations) as excinfo:
                get_mktplace_picks_from_experts(
                    user_id=11,
                    category_count=2,
                    category_buffer=2,
                    candidate_count=2,
                    collection_name=test_pfe,
                    **filter_args,
                )
            featured_first_layer_category.delete()
            assert str(excinfo.value.detail) == "Not enough recommendations"

        def test_get_mktplace_picks_from_experts_case_six(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            # None of featured_first_layer or popular_first_layer exist
            with pytest.raises(NotEnoughRecommendations) as excinfo:
                get_mktplace_picks_from_experts(
                    user_id=999,
                    category_count=2,
                    candidate_count=2,
                    category_buffer=2,
                    collection_name=test_pfe,
                    **filter_args,
                )
            assert str(excinfo.value.detail) == "Not enough recommendations"

        def test_get_mktplace_picks_from_experts_case_seven(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            # Both featured_first_layer and popular_first_layer exist
            # featured_first_layer does not have enough results
            # popular_first_layer does not have enough results
            featured_first_layer_category = FeaturedFirstLayerCategoryByUser(
                user_id=16,
                recommendations=["root//ABC", "root//DEF", "root//GHI"],
                score=[3, 2],
            )
            popular_first_layer_category = PopularFirstLayerCategory(
                group_id=0,
                recommendations=["root//ABC", "root//BBB", "root//CCC"],
                score=[7, 5, 4],
            )
            popular_first_layer_category.save()
            featured_first_layer_category.save()

            with pytest.raises(NotEnoughRecommendations) as excinfo:
                get_mktplace_picks_from_experts(
                    user_id=16,
                    category_count=20,
                    category_buffer=2,
                    candidate_count=2,
                    collection_name=test_pfe,
                    **filter_args,
                )
            featured_first_layer_category.delete()
            popular_first_layer_category.delete()
            assert str(excinfo.value.detail) == "Not enough recommendations"

        def test_get_mktplace_picks_from_experts_case_eight(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            # featured_first_layer exist, not enough results,
            # and popular_first_layer does not exist
            featured_first_layer_category = FeaturedFirstLayerCategoryByUser(
                user_id=16,
                recommendations=["root//ABC", "root//DEF", "root//GHI"],
                score=[3, 2],
            )
            featured_first_layer_category.save()

            with pytest.raises(NotEnoughRecommendations) as excinfo:
                get_mktplace_picks_from_experts(
                    user_id=16,
                    category_count=5,
                    category_buffer=2,
                    candidate_count=2,
                    collection_name=test_pfe,
                    **filter_args,
                )
            featured_first_layer_category.delete()
            assert str(excinfo.value.detail) == "Not enough recommendations"


if __name__ == "__main__":
    pytest.main()
