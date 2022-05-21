import json
import operator
import pytest
import time

from app.main import create_app
from app.main.model.mktplace import (
    UserRecommend,
    PopularItem,
    RecForYouSearch,
    UserDefTrendingNow,
    TrendingNowModel,
    PopularEvent,
    PopularProject,
    PopularSearchKeyword,
    YouMayAlsoBuy,
    EventForYou,
    PopularProductsInProjects,
    YesterdayPopularItem,
    NewProjects,
    FavoriteItem,
    UpcomingEvent,
    ShopNearYou,
    TrendingEvent,
    PopularVisitedEvents,
    PopularFirstLayerCategory,
    PeopleAlsoBuy,
    PopularItemByStore,
    PopularVisitedProjects,
    PopularVisitedItems,
    PopularProductsInEvents,
    ProjectSimilarity,
    RelatedCategoriesByCategory,
    SimilarEvents,
    RelatedQueriesByQuery,
    RelatedQueriesByCategory,
    RelatedCategoriesByQuery,
    TrendingProject,
    FeaturedFirstLayerCategoryByUser,
    PopularItemByCategory,
)
from app.main.util.test_connection import (
    create_local_connection,
    disconnect_local_connection,
)
from app.main.util.global_db_connection import redis_client
from app.main.util.controller_args import mktplace_args

client = create_app(config_name="test").test_client()

filter_url_string = pytest.filter_url_string
test_pfe = pytest.test_pfe
project_filter_url_string = pytest.project_filter_url_string
filter_archive_url_string = pytest.filter_archive_url_string
generate_categories_args_url_string = pytest.generate_categories_args_url_string
recently_view_redis_data = pytest.recently_view_redis_data
test_pab = pytest.test_pab
search_rerank_data = pytest.search_rerank_data


class TestMktplaceController:

    # 200 cases

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            (321, ["2", "1"]),
            (111, ["7", "8"]),
        ],
    )
    def test_recommended_for_you(self, user_id, expected):
        # Case 1: When user exists
        # Case 2: When user doesn't exists
        user_recommend = UserRecommend(
            user_id=321, recommendations=["3", "2", "1"], score=[1, 2, 5]
        )
        popular_item = PopularItem(
            group_id=0, recommendations=["6", "7", "8"], score=[8, 9, 10]
        )
        user_recommend.save()
        popular_item.save()
        response = client.get(
            f"/api/rec/mktplace/recommended_for_you?user_id={user_id}&{filter_url_string}"
        )
        user_recommend.delete()
        popular_item.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_recommended_for_you_bad_request(self):
        response = client.get("/api/rec/mktplace/recommended_for_you?candidate_count=1")
        assert response.status_code == 400

    def test_popular_item(self):
        popular_item = PopularItem(
            group_id=0, recommendations=["1", "2", "3"], score=[6, 1, 4]
        )
        popular_item.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/mktplace/popular_item?group_id=1&candidate_count=3"
            f"&{filter_url_string}"
        )
        popular_item.delete()
        assert operator.eq(expect, json.loads(response.data))

    @pytest.mark.parametrize(
        "redis_similar_items",
        ["fgm_similar_items"],
        indirect=True,
    )
    def test_similar_items(self, redis_similar_items):
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/mktplace/similar_items?item_id=item1&candidate_count=2"
            f"&{filter_url_string}"
        )
        assert operator.eq(expect, json.loads(response.data))

    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("abc", ["1", "2"]),
            ("def", []),
        ],
    )
    def test_popular_item_by_category(self, category_path, expected):
        # Case 1: With popular item by category data
        # Case 2: Without popular item by category data
        popular_item_by_category = PopularItemByCategory(
            category_path="abc", recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        popular_item_by_category.save()
        response = client.get(
            f"/api/rec/mktplace/popular_item_by_category?category_path={category_path}&candidate_count=2"
            f"&{filter_url_string}"
        )
        popular_item_by_category.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_popular_item_by_category_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/popular_item_by_category?candidate_count=3"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "zip_code, expected",
        [
            ("75037", ["20394", "55785", "73585"]),
            ("43215", []),
        ],
    )
    def test_shop_near_you(self, zip_code, expected):
        shop_near_you = ShopNearYou(
            zip_code="75037",
            recommendations=["20394", "55785", "73585"],
        )
        shop_near_you.save()
        response = client.get(f"/api/rec/mktplace/shop_near_you?zip_code={zip_code}")
        shop_near_you.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_shop_near_you_bad_request(self):
        response = client.get("/api/rec/mktplace/shop_near_you")
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "mongo_filter_scored_item_with_collection_name",
        [test_pab],
        indirect=True,
    )
    def test_search_people_also_buy(
        self, mongo_filter_scored_item_with_collection_name
    ):
        expect = ["2", "1", "4"]
        response = client.get(
            f"/api/rec/mktplace/search_people_also_buy?items_scores=2%203&items_id_list=101%20102"
            f"&candidate_count=3&collection_name=test_pab&{filter_url_string}"
        )
        assert operator.eq(expect, json.loads(response.data))

    @pytest.mark.parametrize(
        "group_id, expected",
        [
            (0, ["1", "2"]),
            (1, []),
        ],
    )
    def test_mktplace_trending_project(self, group_id, expected):
        # Case 1: when recommendations exist
        # Case 2: when no recommendations exist
        trending_project = TrendingProject(
            group_id=group_id, recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        trending_project.save()
        response = client.get(
            f"/api/rec/mktplace/trending_project?candidate_count=2"
            f"&{project_filter_url_string}"
        )
        trending_project.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_mktplace_trending_project_bad_request(self):
        response = client.get("/api/rec/mktplace/trending_project?candidate_count=None")
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "mongo_filter_scored_item_with_collection_name",
        [test_pab],
        indirect=True,
    )
    def test_search_people_also_buy_value_error(
        self, mongo_filter_scored_item_with_collection_name
    ):
        response = client.get(
            f"/api/rec/mktplace/search_people_also_buy?items_id_list=1001%20201&items_scores=%20&candidate_count=2"
            f"&collection_name=test_pab&{filter_url_string}"
        )
        assert json.loads(response.data)["message"] == "Input Parameters Value Error"

    @pytest.mark.parametrize(
        "mongo_filter_scored_item_with_collection_name",
        [test_pab],
        indirect=True,
    )
    def test_search_people_also_buy_with_default_scores(
        self, mongo_filter_scored_item_with_collection_name
    ):
        expect = ["2", "1", "4"]
        response = client.get(
            f"/api/rec/mktplace/search_people_also_buy?items_id_list=101%20102"
            f"&candidate_count=3&collection_name=test_pab&{filter_url_string}"
        )
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_search_keyword(self):
        popular_search_keyword = PopularSearchKeyword(
            group_id=0, recommendations=["Top", "Search", "Word"], score=[7, 6, 5]
        )
        popular_search_keyword.save()
        expect = ["Top", "Search", "Word"]
        response = client.get(
            f"/api/rec/mktplace/popular_search_keyword?candidate_count=3"
        )
        popular_search_keyword.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_top_picks(self):
        # add fake top picks items
        redis_top_pics_hkey = mktplace_args["top_picks_args"]["redis_hash_key"][
            "default"
        ]
        redis_client.hset(
            redis_top_pics_hkey,
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
        response = client.get(
            f"/api/rec/mktplace/top_picks?user_id=3759&candidate_count=3"
            f"&{filter_url_string}"
        )
        redis_client.delete(redis_top_pics_hkey)
        assert operator.eq(expect, json.loads(response.data))

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            (101, ["101", "102", "103"]),
            (23, ["13", "14", "15"]),
        ],
    )
    def test_rec_for_you_search(self, user_id, expected):
        # Case 1: When user exists
        # Case 2: When user doesn't exists
        rec_for_you_search = RecForYouSearch(
            user_id=101, recommendations=["101", "102", "103"], score=[4, 5, 8]
        )
        popular_search_keywords = PopularSearchKeyword(
            group_id=0, recommendations=["13", "14", "15"], score=[7, 6, 5]
        )
        rec_for_you_search.save()
        popular_search_keywords.save()
        response = client.get(f"/api/rec/mktplace/rec_for_you_search?user_id={user_id}")
        rec_for_you_search.delete()
        popular_search_keywords.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_rec_for_you_search_bad_request(self):
        response = client.get("/api/rec/mktplace/rec_for_you_search?candidate_count=n")
        assert response.status_code == 400

    def test_search_rerank(self, redis_search_rerank):
        # The item vector in the redis is of size(1, 300) but here we are using size(1, 10) vector to test
        data = search_rerank_data[0]
        mimetype = "application/json"
        headers = {"Content-Type": mimetype, "Accept": mimetype}
        expect = {"1022": 0.4082482904638631, "1011": 0.22360679774997896}
        response = client.post(
            "/api/rec/mktplace/search_rerank", data=json.dumps(data), headers=headers
        )
        assert operator.eq(expect, json.loads(response.data))

    @pytest.mark.parametrize(
        "category_path, recommendations, expected",
        [
            ("abc", ["1", "2", "3"], ["1", "2"]),
            ("def", [], []),
        ],
    )
    def test_user_defined_trending_now(self, category_path, recommendations, expected):
        # Case 1: Recommendations exist
        # Case 2: Empty list recommendations
        user_def_tn = UserDefTrendingNow(
            category_path=category_path, recommendations=recommendations
        )
        user_def_tn.save()
        response = client.get(
            f"/api/rec/mktplace/user_defined_trending_now?category_path={category_path}"
            f"&candidate_count=3&{filter_url_string}"
        )
        user_def_tn.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_user_defined_trending_now_404(self):
        response = client.get(
            f"/api/rec/mktplace/user_defined_trending_now?category_path=root%2F%2FCustom%20Frames"
            f"&candidate_count=2&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_user_defined_trending_now_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/user_defined_trending_now?candidate_count=1"
        )
        assert response.status_code == 400

    def test_add_user_defined_trending_now(self):
        expect = {
            "category_path": "root//Planners",
            "recommendations": ["462525", "57256", "562758", "52645"],
        }
        response = client.put(
            f"/api/rec/mktplace/add_user_defined_trending_now?category_path=root%2F%2FPlanners&rec_item_ids=462525%2C57256"
            f"%2C562758%2C52645"
        )
        # Compare new user defined trending now items that are inserted into DB with expected result
        user_def_tn_obj = UserDefTrendingNow.objects(
            category_path="root//Planners"
        ).get()
        user_def_tn_obj.save()
        user_def_tn_obj.delete()
        assert operator.eq(expect, json.loads(response.data))
        assert operator.eq(expect["recommendations"], user_def_tn_obj.recommendations)

    @pytest.mark.parametrize(
        "category_path, recommendations, expected",
        [
            ("abc", ["5", "8", "9"], ["8", "9"]),
            ("def", [], []),
        ],
    )
    def test_trending_now_model(self, category_path, recommendations, expected):
        # Case 1: Recommendations exist
        # Case 2: Empty list recommendations
        trending_now = TrendingNowModel(
            category_path=category_path, recommendations=recommendations
        )
        trending_now.save()
        response = client.get(
            f"/api/rec/mktplace/trending_now_model?category_path={category_path}"
            f"&candidate_count=3&{filter_url_string}"
        )
        trending_now.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_trending_now_model_404(self):
        response = client.get(
            f"/api/rec/mktplace/trending_now_model?category_path=root%2F%2FShopping%20Categories"
            f"&candidate_count=2&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_trending_now_model_bad_request(self):
        response = client.get("/api/rec/mktplace/trending_now_model?candidate_count=1")
        assert response.status_code == 400

    def test_trending_now(self):
        mod_trending_now = TrendingNowModel(
            category_path="root//Shop Categories",
            recommendations=["4", "5"],
        )
        user_def_tn = UserDefTrendingNow(
            category_path="root//Shop Categories",
            recommendations=["1", "2", "3"],
        )
        mod_trending_now.save()
        user_def_tn.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/mktplace/trending_now?category_path=root%2F%2FShop%20Categories"
            f"&candidate_count=3&{filter_url_string}"
        )
        mod_trending_now.delete()
        user_def_tn.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_trending_now_all_category(self):
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
        response = client.get(
            f"/api/rec/mktplace/trending_now_all_category?user_defined_trending_now=fgm_udf_tn_coll"
            f"&trending_now=fgm_tn_coll&candidate_count=2&{filter_url_string}"
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, json.loads(response.data))

    def test_event_for_you(
        self,
        mock_filter_no_schedule_events_in_mongo,
        mock_filter_archived_events_in_mongo,
    ):
        event_recommend = EventForYou(
            user_id=17, recommendations=["1", "2", "3"], score=[1, 2, 3]
        )
        event_recommend.save()
        expect = ["1", "2", "3"]
        response = client.get(
            "/api/rec/mktplace/event_for_you?user_id=17&candidate_count=2&event_type=IN_STORE"
        )
        event_recommend.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_event(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        popular_event = PopularEvent(
            group_id=5, recommendations=["1009", "1001"], score=[3, 6]
        )
        popular_event.save()
        response = client.get(
            "/api/rec/michaels/popular_event?group_id=99&event_type=ONLINE"
        )
        popular_event.delete()
        assert response.status_code == 404

    # 404 cases
    def test_popular_item_404(self):
        popular_item = PopularItem(
            group_id="1", recommendations=["100009", "100001"], score=[5, 4]
        )
        popular_item.save()
        response = client.get(
            f"/api/rec/mktplace/popular_item/group_id='2'&{filter_url_string}"
        )
        popular_item.delete()
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "redis_similar_items",
        ["fgm_similar_items"],
        indirect=True,
    )
    def test_similar_items_404(self, redis_similar_items):
        response = client.get(
            f"/api/rec/mktplace/similar_items?item_id=102&candidate_count=2&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_search_people_also_buy_404(self):
        response = client.get(
            f"/api/rec/mktplace/search_people_also_buy?items_scores=2%203&items_id_list=666%20999&candidate_count=3"
            f"&collection_name=test_col&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_popular_search_keyword_404(self):
        response = client.get(
            f"/api/rec/mktplace/popular_search_keyword?candidate_count=3"
        )
        assert response.status_code == 404

    def test_event_for_you_404(
        self,
        mock_filter_no_schedule_events_in_mongo,
        mock_filter_archived_events_in_mongo,
    ):
        event_recommend = EventForYou(
            user_id=666, recommendations=["5001", "5002", "5003"], score=[5, 6, 7]
        )
        popular_event = PopularEvent(
            group_id=0, recommendations=["1", "2", "3"], score=[1, 2]
        )
        event_recommend.save()
        popular_event.save()
        response = client.get(
            f"/api/rec/mktplace/event_for_you?user_id=123&event_type=IN_STORE&{filter_archive_url_string}"
        )
        expect = ["1", "2", "3"]
        popular_event.delete()
        event_recommend.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_top_picks_404(self):
        response = client.get(
            f"/api/rec/mktplace/top_picks?user_id=5678&candidate_count=3&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_search_rerank_404(self, redis_search_rerank):
        # The item vector in the redis is of size(1, 300) but here we are using size(1, 10) vector to test
        data = search_rerank_data[3]
        mimetype = "application/json"
        headers = {"Content-Type": mimetype, "Accept": mimetype}
        response = client.post(
            "/api/rec/mktplace/search_rerank",
            data=json.dumps(data),
            headers=headers,
        )
        assert response.status_code == 404

    def test_add_user_defined_trending_now_404(self):
        # Case where list of recommendations is empty
        expect = {"category_path": "root//Planners", "recommendations": []}
        response = client.put(
            f"/api/rec/mktplace/add_user_defined_trending_now?category_path=root%2F%2FPlanners"
        )
        user_def_tn_obj = UserDefTrendingNow.objects(
            category_path="root//Planners"
        ).get()
        user_def_tn_obj.save()
        user_def_tn_obj.delete()
        assert operator.eq(expect, json.loads(response.data))
        assert operator.eq(expect["recommendations"], user_def_tn_obj.recommendations)

    def test_trending_now_404(self):
        trending_now = TrendingNowModel(
            category_path="root//Shop Categories",
            recommendations=["1", "2"],
        )
        trending_now.save()
        response = client.get(
            f"/api/rec/mktplace/trending_now_model?category_path=root%2F%2FShopping%20Categories"
            f"&candidate_count=2&{filter_url_string}"
        )
        trending_now.delete()
        assert json.loads(response.data) == []

    def test_trending_now_all_category_404(self):
        local_conn1, local_col1 = create_local_connection(
            collection_name="fgm_udf_tn_coll"
        )
        local_conn2, local_col2 = create_local_connection(collection_name="fgm_tn_coll")
        response = client.get(
            f"/api/rec/mktplace/trending_now_all_category?user_defined_trending_now=udf_tn_coll"
            f"&trending_now=fgm_tn_coll&{filter_url_string}"
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert json.loads(response.data) == []

    def test_popular_event_404(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        popular_event = PopularEvent(
            group_id=5, recommendations=["1009", "1001"], score=[3, 6]
        )
        popular_event.save()
        response = client.get(
            "/api/rec/michaels/popular_event?group_id=99&event_type=ONLINE"
        )
        popular_event.delete()
        assert response.status_code == 404

    def test_popular_project_404(self):
        popular_project = PopularProject(
            group_id=1, recommendations=["25678", "27654"], score=[2, 4]
        )
        popular_project.save()
        response = client.get("/api/rec/mktplace/popular_project")
        popular_project.delete()
        assert response.status_code == 404

    # Bad request cases
    def test_similar_item_bad_request(self):
        response = client.get("/api/rec/mktplace/similar_items?")
        assert response.status_code == 400

    def test_popular_item_bad_request(self):
        response = client.get("/api/rec/mktplace/popular_item?candidate_count=None")
        assert response.status_code == 400

    def test_add_user_defined_trending_now_bad_request(self):
        response = client.put("/api/rec/mktplace/add_user_defined_trending_now")
        assert response.status_code == 400

    def test_trending_now_bad_request(self):
        response = client.get("/api/rec/mktplace/trending_now?candidate_count=1")
        assert response.status_code == 400

    def test_trending_now_all_category_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/trending_now_all_category?candidate_count=c"
        )
        assert response.status_code == 400

    def test_top_picks_bad_request(self):
        response = client.get(f"/api/rec/mktplace/top_picks")
        assert response.status_code == 400

    def test_search_term_categories(self):
        response = client.get(
            f"/api/rec/mktplace/search_term_categories?{generate_categories_args_url_string}"
        )
        expect = ["Party//Holiday Parties//Christmas Party"]
        result = json.loads(response.data)
        assert operator.eq(expect, result)

    def test_search_people_also_buy_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/search_people_also_buy?candidate_count=8"
        )
        assert response.status_code == 400

    def test_popular_search_keyword_bad_request(self):
        response = client.get(
            f"/api/rec/mktplace/popular_search_keyword?candidate_count=h"
        )
        assert response.status_code == 400

    def test_event_for_you_bad_request(self):
        response = client.get("/api/rec/mktplace/event_for_you?candidate_count=1")
        assert response.status_code == 400

    def test_search_rerank_bad_request(self):
        response = client.post("/api/rec/mktplace/search_rerank")
        assert response.status_code == 400

    def test_popular_event_bad_request(self):
        response = client.get("/api/rec/mktplace/popular_event?candidate_count=None")
        assert response.status_code == 400

    def test_popular_project_bad_request(self):
        response = client.get("/api/rec/mktplace/popular_project?candidate_count=None")
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "mock_redis_client",
        [recently_view_redis_data],
        indirect=True,
    )
    def test_recently_viewed_streaming(self, mock_redis_client):
        rec_api_redis_client = mock_redis_client
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/mktplace/recently_viewed_streaming?user_id=fgm_streaming_recently_view_123"
            f"&candidate_count=2&{filter_url_string}"
        )
        assert operator.eq(expect, json.loads(response.data))

    @pytest.mark.parametrize(
        "mock_redis_client",
        [None],
        indirect=True,
    )
    def test_recently_viewed_streaming_404(self, mock_redis_client):
        rec_api_redis_client = mock_redis_client
        response = client.get(
            f"/api/rec/mktplace/recently_viewed_streaming?user_id=fgm_streaming_recently_view_123"
            f"&candidate_count=3&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_recently_viewed_streaming_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/recently_viewed_streaming?candidate_count=3"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            ("777", ["1", "2"]),
            ("99", ["7", "8"]),
        ],
    )
    def test_you_may_also_buy(self, user_id, expected):
        # Case 1: With user id
        # Case 2: Without user id
        you_may_also_buy = YouMayAlsoBuy(user_id="777", recommendations=["1", "2", "3"])
        popular_item = PopularItem(
            group_id=0, recommendations=["6", "7", "8"], score=[7, 6, 5]
        )
        you_may_also_buy.save()
        popular_item.save()
        response = client.get(
            f"/api/rec/mktplace/you_may_also_buy?user_id={user_id}&candidate_count=3"
            f"&{filter_url_string}"
        )
        you_may_also_buy.delete()
        popular_item.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_you_may_also_buy_bad_request(self):
        response = client.get("/api/rec/mktplace/you_may_also_buy?candidate_count=3")
        assert response.status_code == 400

    def test_mktplace_popular_products_in_projects(self):
        popular_products_in_projects = PopularProductsInProjects(
            group_id=0, recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        popular_products_in_projects.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/mktplace/popular_products_in_projects?candidate_count=3"
            f"&{filter_url_string}"
        )
        popular_products_in_projects.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_mktplace_popular_products_in_projects_404(self):
        response = client.get(
            f"/api/rec/mktplace/popular_products_in_projects?candidate_count=2"
            f"&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_mktplace_popular_products_in_projects_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/popular_products_in_projects?candidate_count"
        )
        assert response.status_code == 400

    def test_yesterday_popular_item(self):
        yesterday_popular_item = YesterdayPopularItem(
            group_id=0, recommendations=["2", "4", "6", "8"], score=[7, 6, 5, 4]
        )
        yesterday_popular_item.save()
        expect = ["2", "4", "8"]
        response = client.get(
            f"/api/rec/mktplace/yesterday_popular_item?{filter_url_string}"
        )
        yesterday_popular_item.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_yesterday_popular_item_404(self):
        response = client.get(
            f"/api/rec/mktplace/yesterday_popular_item?{filter_url_string}"
        )
        assert response.status_code == 404

    def test_yesterday_popular_item_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/yesterday_popular_item?candidate_count"
        )
        assert response.status_code == 400

    def test_mktplace_new_projects(self):
        new_projects = NewProjects(group_id=0, recommendations=["1", "2", "3"])
        new_projects.save()

        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/mktplace/new_projects?candidate_count=2&{project_filter_url_string}"
        )
        new_projects.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_mktplace_new_projects_404(self):
        response = client.get("/api/rec/mktplace/new_projects?candidate_count=2")
        assert response.status_code == 404

    def test_mktplace_new_projects_bad_request(self):
        response = client.get("/api/rec/mktplace/new_projects?candidate_count")
        assert response.status_code == 400

    def test_mktplace_favorite_item(self):
        favorite_item = FavoriteItem(
            group_id=0, recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        favorite_item.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/mktplace/favorite_item?candidate_count=3&{filter_url_string}"
        )
        favorite_item.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_mktplace_favorite_item_404(self):
        response = client.get(f"/api/rec/mktplace/favorite_item?candidate_count=2")
        assert response.status_code == 404

    def test_mktplace_favorite_item_bad_request(self):
        response = client.get("/api/rec/mktplace/favorite_item?candidate_count")
        assert response.status_code == 400

    def test_upcoming_event(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        test_timestamp = int(time.time()) % (24 * 3600) // 900 * 900
        upcoming_event = UpcomingEvent(
            timestamp=test_timestamp, events_id=["1", "2", "3"], schedules_id=[1, 2, 3]
        )
        upcoming_event.save()
        expect = [{"event_id": ["1", "2", "3"], "schedules_id": [1, 2, 3]}]
        response = client.get(
            "/api/rec/mktplace/upcoming_event?candidate_count=3&event_type=ONLINE"
        )
        upcoming_event.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_mktplace_upcoming_event_404(self):
        response = client.get(
            "/api/rec/mktplace/upcoming_event?candidate_count=2&event_type=ONLINE"
        )
        assert response.status_code == 404

    def test_mktplace_upcoming_event_bad_request(self):
        response = client.get("/api/rec/mktplace/upcoming_event?candidate_count")
        assert response.status_code == 400

    def test_trending_event(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        trending_event = TrendingEvent(
            group_id=0, recommendations=["1", "2", "3"], score=[1, 2, 3]
        )
        trending_event.save()
        expect = ["1", "2", "3"]
        response = client.get(
            "/api/rec/mktplace/trending_event?group_id=0&candidate_count=3&event_type=ONLINE"
        )
        trending_event.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_trending_event_404(self):
        response = client.get(
            "/api/rec/mktplace/trending_event?group_id=12&event_type=ONLINE"
        )
        assert response.status_code == 404

    def test_trending_event_bad_request(self):
        response = client.get("/api/rec/mktplace/trending_event?candidate_count=None")
        assert response.status_code == 400

    def test_popular_visited_events(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        popular_visited_events = PopularVisitedEvents(
            group_id=0,
            recommendations=["1001", "1002", "1003"],
            score=[12, 5, 1],
        )
        popular_visited_events.save()
        expect = ["1", "2", "3"]
        response = client.get(
            "/api/rec/mktplace/popular_visited_events?candidate_count=2&event_type=IN_STORE"
        )
        popular_visited_events.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_visited_events_404(self):
        response = client.get(
            "/api/rec/mktplace/popular_visited_events&event_type=IN_STORE"
        )
        assert response.status_code == 404

    def test_popular_visited_events_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/popular_visited_events?candidate_count="
        )
        assert response.status_code == 400

    def test_popular_first_layer_category(self):
        popular_first_layer_category = PopularFirstLayerCategory(
            group_id=0,
            recommendations=["root//AA", "root//BB", "root//CC"],
            score=[12, 5, 1],
        )
        popular_first_layer_category.save()
        expect = ["root//AA", "root//BB"]
        response = client.get(
            "/api/rec/mktplace/popular_first_layer_category?candidate_count=2"
        )
        popular_first_layer_category.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_first_layer_category_404(self):
        response = client.get("/api/rec/mktplace/popular_first_layer_category")
        assert response.status_code == 404

    def test_popular_first_layer_category_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/popular_first_layer_category?candidate_count="
        )
        assert response.status_code == 400

    def test_mktplace_popular_item_by_store(self):
        popular_item_by_store = PopularItemByStore(
            store_id=234, recommendations=["1", "2", "3"], score=[8, 7, 6]
        )
        popular_item_by_store.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/mktplace/popular_item_by_store?store_id=234&candidate_count=2"
            f"&{filter_url_string}"
        )
        popular_item_by_store.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_mktplace_popular_item_by_store_404(self):
        response = client.get(
            f"/api/rec/mktplace/popular_item_by_store?store_id=555&candidate_count=2"
            f"&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_mktplace_popular_item_by_store_bad_request(self):
        response = client.get(
            f"/api/rec/mktplace/popular_item_by_store?candidate_count=None"
            f"&{filter_url_string}"
        )
        assert response.status_code == 400

    def test_people_also_buy(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="333", recommendations=["1", "2", "3"], score=[4, 5, 7]
        )
        people_also_buy.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/mktplace/people_also_buy?item_id=333&candidate_count=3"
            f"&{filter_url_string}"
        )
        people_also_buy.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_people_also_buy_404(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="75", recommendations=["108", "131"], score=[5, 8]
        )
        people_also_buy.save()
        response = client.get(
            f"/api/rec/mktplace/people_also_buy?item_id=3&candidate_count=2"
            f"&{filter_url_string}"
        )
        people_also_buy.delete()
        assert json.loads(response.data) == []

    def test_people_also_buy_bad_request(self):
        response = client.get("/api/rec/mktplace/people_also_buy?candidate_count=3")
        assert response.status_code == 400

    def test_popular_visited_projects(self):
        popular_visited_projects = PopularVisitedProjects(
            group_id=0,
            recommendations=["1", "2", "3"],
            score=[12, 5, 1],
        )
        popular_visited_projects.save()
        expect = ["1", "2"]
        response = client.get(
            "/api/rec/mktplace/popular_visited_projects?candidate_count=2"
        )
        popular_visited_projects.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_visited_projects_404(self):
        response = client.get("/api/rec/mktplace/popular_visited_projects")
        assert response.status_code == 404

    def test_popular_visited_projects_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/popular_visited_projects?candidate_count="
        )
        assert response.status_code == 400

    def test_popular_visited_items(self):
        popular_visited_items = PopularVisitedItems(
            group_id=0,
            recommendations=["1", "2", "3"],
            score=[12, 5, 1],
        )
        popular_visited_items.save()
        expect = ["1", "2"]
        response = client.get(
            "/api/rec/mktplace/popular_visited_items?candidate_count=2"
        )
        popular_visited_items.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_visited_items_404(self):
        response = client.get("/api/rec/mktplace/popular_visited_items")
        assert response.status_code == 404

    def test_popular_visited_items_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/popular_visited_items?candidate_count="
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "mongo_filter_scored_item_with_collection_name",
        ["fgm_purchased_together"],
        indirect=True,
    )
    def test_shopping_cart_bundle(self, mongo_filter_scored_item_with_collection_name):
        expect = ["2", "1"]
        response = client.get(
            f"/api/rec/mktplace/shopping_cart_bundle?items_id_list=103%20104%20105&candidate_count=4"
            f"&{filter_url_string}"
        )
        assert operator.eq(expect, json.loads(response.data))

    def test_shopping_cart_bundle_404(self):
        expect = []
        response = client.get(
            "/api/rec/mktplace/shopping_cart_bundle?items_id_list=1001&candidate_count=4"
        )
        assert operator.eq(expect, json.loads(response.data))

    def test_shopping_cart_bundle_bad_request(self):
        response = client.get("/api/rec/mktplace/shopping_cart_bundle?candidate_count=")
        assert response.status_code == 400

    def test_mktplace_popular_products_in_events(self):
        popular_products_in_events = PopularProductsInEvents(
            group_id=0, recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        popular_products_in_events.save()

        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/mktplace/popular_products_in_events?candidate_count=3"
            f"&{filter_url_string}"
        )
        popular_products_in_events.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_mktplace_popular_products_in_events_404(self):
        response = client.get(
            f"/api/rec/mktplace/popular_products_in_events?candidate_count=2"
            f"&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_mktplace_popular_products_in_events_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/popular_products_in_events?candidate_count"
        )
        assert response.status_code == 400

    def test_similar_projects(self):
        project_similar = ProjectSimilarity(
            external_id="1083",
            recommendations=["1", "2", "3"],
            score=[5, 4, 7],
        )
        project_similar.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/mktplace/similar_projects?external_id=1083&candidate_count=2&{project_filter_url_string}"
        )
        project_similar.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_similar_projects_404(self):
        response = client.get(
            "/api/rec/mktplace/similar_projects?external_id=1110&candidate_count=2"
        )
        assert response.status_code == 404

    def test_similar_projects_bad_request(self):
        response = client.get("/api/rec/mktplace/similar_projects?candidate_count=11")
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("category_input", ["category1", "category2"]),
            ("invalid_category_input", []),
        ],
    )
    def test_mktplace_related_categories_by_category(self, category_path, expected):
        related_categories_by_category = RelatedCategoriesByCategory(
            category_path="category_input",
            recommendations=["category1", "category2", "category3"],
        )
        related_categories_by_category.save()
        response = client.get(
            f"/api/rec/mktplace/related_categories_by_category?category_path={category_path}"
            f"&candidate_count=2"
        )
        related_categories_by_category.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_mktplace_related_categories_by_category_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/related_categories_by_category?candidate_count"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("category_input", ["query1", "query2"]),
            ("invalid_category_input", []),
        ],
    )
    def test_mktplace_related_queries_by_category(self, category_path, expected):
        related_queries_by_category = RelatedQueriesByCategory(
            category_path="category_input",
            recommendations=["query1", "query2", "query3"],
        )
        related_queries_by_category.save()
        response = client.get(
            f"/api/rec/mktplace/related_queries_by_category?category_path={category_path}"
            f"&candidate_count=2"
        )
        related_queries_by_category.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_mktplace_related_queries_by_category_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/related_queries_by_category?candidate_count"
        )
        assert response.status_code == 400

    def test_similar_events(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        event_similar = SimilarEvents(
            event_id=103, recommendations=["1", "2", "3"], score=[7, 8, 6]
        )
        event_similar.save()
        expect = ["1", "2", "3"]
        response = client.get(
            "/api/rec/mktplace/similar_events?event_id=103&candidate_count=3&event_type=ONLINE"
        )
        event_similar.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_similar_events_404(self):
        event_similar = SimilarEvents(
            event_id="10083", recommendations=["10622", "10585"], score=[9, 10]
        )
        event_similar.save()
        response = client.get(
            "/api/rec/mktplace/similar_events?event_id=10088&candidate_count=2&event_type=ONLINE"
        )
        event_similar.delete()
        assert response.status_code == 404

    def test_similar_events_bad_request(self):
        response = client.get("/api/rec/mktplace/similar_events?candidate_count=11")
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "mongo_similar_items_by_popularity",
        ["fgm_popular_master_items"],
        indirect=True,
    )
    def test_mktplace_similar_items_by_popularity(
        self, mongo_similar_items_by_popularity
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

        expected = ["4", "1", "2"]
        response = client.get(
            f"/api/rec/mktplace/similar_items_by_popularity?candidate_count=5"
            f"&item_id=item1&collection_name={collection_name}&{filter_url_string}"
        )
        redis_client.delete(redis_similar_items_hkey)
        assert operator.eq(expected, json.loads(response.data))

    def test_mktplace_similar_items_by_popularity_not_found(self):
        collection_name = "fgm_popular_master_items"
        expected = []
        response = client.get(
            f"/api/rec/mktplace/similar_items_by_popularity?candidate_count=2"
            f"&item_id=item1&collection_name={collection_name}&{filter_url_string}"
        )
        assert operator.eq(expected, json.loads(response.data))

    def test_mktplace_similar_items_by_popularity_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/similar_items_by_popularity?candidate_count"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "query_keyword, expected",
        [("query_input", ["1", "2", "3"]), ("invalid_query_input", [])],
    )
    def test_mktplace_related_queries_by_query(self, query_keyword, expected):
        related_queries = RelatedQueriesByQuery(
            query="query_input", recommendations=["1", "2", "3"], score=[7, 6, 5]
        )

        related_queries.save()
        response = client.get(
            f"/api/rec/mktplace/related_queries_by_query?candidate_count=3&query_keyword={query_keyword}"
        )
        related_queries.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_mktplace_related_queries_by_query_bad_request(self):
        response = client.get("/api/rec/mktplace/related_queries_by_query")
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "query_keyword, expected",
        [
            ("query_keyword", ["category1", "category2"]),
            ("invalid_query_keyword", []),
        ],
    )
    def test_mktplace_related_categories_by_query(self, query_keyword, expected):
        related_categories_by_query = RelatedCategoriesByQuery(
            query="query_keyword",
            recommendations=["category1", "category2", "category3"],
            score=[1, 2, 3],
        )
        related_categories_by_query.save()
        response = client.get(
            f"/api/rec/mktplace/related_categories_by_query?query_keyword={query_keyword}"
            f"&candidate_count=2"
        )
        related_categories_by_query.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_mktplace_related_categories_by_query_bad_request(self):
        response = client.get(
            "/api/rec/mktplace/related_categories_by_query?candidate_count"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "mongo_filter_inactive_item_with_collection_name, mongo_filter_inactive_category",
        [(test_pfe, test_pfe)],
        indirect=True,
    )
    class TestMktplacePicksFromExpectsController:
        def test_picks_from_experts(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            featured_first_layer_category = FeaturedFirstLayerCategoryByUser(
                user_id=169,
                recommendations=["root//ABC", "root//DEF"],
                score=[3, 2],
            )
            popular_first_layer_category = PopularFirstLayerCategory(
                group_id=0,
                recommendations=["root//AAA", "root//BBB", "root//CCC"],
                score=[7, 5, 4],
            )
            popular_first_layer_category.save()
            featured_first_layer_category.save()
            expect = {"root//ABC": ["1", "4"], "root//DEF": ["2", "7"]}
            response = client.get(
                f"/api/rec/mktplace/picks_from_experts?user_id=169&category_count=2&candidate_count=2"
                f"&category_buffer=2&collection_name={test_pfe}&{filter_url_string}"
            )
            featured_first_layer_category.delete()
            popular_first_layer_category.delete()
            assert operator.eq(expect, json.loads(response.data))

        def test_picks_from_experts_404(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            # If user has not logged in
            popular_first_layer_category = PopularFirstLayerCategory(
                group_id=0,
                recommendations=["root//ABC", "root//DEF", "root//CCC"],
                score=[7, 5, 4],
            )
            popular_first_layer_category.save()
            expect = {"root//ABC": ["1", "4"], "root//DEF": ["2", "7"]}
            response = client.get(
                f"/api/rec/mktplace/picks_from_experts?category_count=2"
                f"&candidate_count=2&collection_name={test_pfe}&{filter_url_string}"
            )
            popular_first_layer_category.delete()
            assert operator.eq(expect, json.loads(response.data))

        def test_picks_from_experts_bad_request(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            response = client.get(
                "/api/rec/mktplace/picks_from_experts?candidate_count=v"
            )
            assert response.status_code == 400


if __name__ == "__main__":
    pytest.main()
