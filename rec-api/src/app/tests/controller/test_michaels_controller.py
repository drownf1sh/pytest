import json
import operator
import pytest
import datetime
import time

from app.main import create_app
from app.main.model.michaels import (
    UserRecommend,
    PurchaseBundle,
    FeaturedCategory,
    BuyItAgain,
    PeopleAlsoBuy,
    PeopleAlsoView,
    SeasonalTopPicks,
    ProjectUseThis,
    ProjectInspiration,
    PopularItem,
    ProjectSimilarity,
    BuyItAgainMPG,
    RecForYouSearch,
    TrendingNowModel,
    UserDefTrendingNow,
    FeaturedFirstLayerCategoryByUser,
    PopularFirstLayerCategory,
    PopularSearchKeyword,
    YouMayAlsoBuy,
    PopularItemByStore,
    PopularProductsInProjects,
    YesterdayPopularItem,
    NewProjects,
    UpcomingEvent,
    FavoriteItemForYou,
    TrendingEvent,
    PopularClearanceCategory,
    PopularSaleCategory,
    PopularClearanceItem,
    PopularSaleItem,
    PopularVisitedEvents,
    FavoriteItem,
    PopularVisitedProjects,
    PopularVisitedItems,
    SimilarItemsInSameStore,
    PopularProductsInEvents,
    RelatedCategoriesByCategory,
    RelatedQueriesByQuery,
    RelatedQueriesByCategory,
    RelatedCategoriesByQuery,
    TrendingProject,
    PopularItemByCategory,
    ViewedTogether,
)
from app.main.model.michaels import EventForYou, SimilarEvents, PopularEvent
from app.main.model.michaels import PopularProject, PopularCategory
from app.main.util.test_connection import (
    create_local_connection,
    disconnect_local_connection,
)
from app.main.util.global_db_connection import redis_client
from app.main.util.controller_args import michaels_args

client = create_app(config_name="test").test_client()

filter_url_string = pytest.filter_url_string
test_pfe = pytest.test_pfe
project_filter_url_string = pytest.project_filter_url_string
filter_archive_url_string = pytest.filter_archive_url_string
filter_badges_url_string = pytest.filter_badges_url_string
similar_items_for_bundle_args_url_string = (
    pytest.similar_items_for_bundle_args_url_string
)
recently_view_redis_data = pytest.recently_view_redis_data
now = datetime.date.today()
test_pab = pytest.test_pab
search_rerank_data = pytest.search_rerank_data


class TestMichaelsController:
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
            f"/api/rec/michaels/recommended_for_you?user_id={user_id}&{filter_url_string}"
        )
        user_recommend.delete()
        popular_item.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_recommended_for_you_bad_request(self):
        response = client.get("/api/rec/michaels/recommended_for_you?candidate_count=1")
        assert response.status_code == 400

    def test_favorite_item_for_you(self):
        favorite_item_for_you = FavoriteItemForYou(
            user_id="125", recommendations=["1", "2", "3"], score=[7, 8, 9]
        )
        favorite_item_for_you.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/favorite_item_for_you?user_id=125"
            f"&candidate_count=3&{filter_url_string}"
        )

        favorite_item_for_you.delete()
        assert operator.eq(expect, json.loads(response.data))

    @pytest.mark.parametrize(
        "redis_similar_items",
        ["mik_similar_items"],
        indirect=True,
    )
    def test_similar_items(self, redis_similar_items):
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/similar_items?item_id=item1&candidate_count=2"
            f"&{filter_url_string}"
        )
        assert operator.eq(expect, json.loads(response.data))

    def test_purchased_together(self):
        purchase_bundle = PurchaseBundle(
            item_id="10062488",
            recommendations=["1", "2", "3"],
            score=[4, 6, 8],
        )
        purchase_bundle.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/purchased_together?item_id=10062488&candidate_count=2"
            f"&{filter_url_string}"
        )
        purchase_bundle.delete()
        assert operator.eq(expect, json.loads(response.data))

    @pytest.mark.parametrize(
        "item_id_pt, item_id_vt, expect",
        [
            ("15374", "15374", ["8", "4", "7", "2", "1"]),
            ("15374", "11348", ["1", "2", "4", "8"]),
            ("11348", "15374", ["4", "7", "8"]),
            ("13825", "25672", []),
        ],
    )
    def test_purchased_and_viewed_together(self, item_id_pt, item_id_vt, expect):
        # Case 1: Both Purchased together and Viewed together items exist
        # Case 2: Purchased together exists but no viewed together
        # Case 3: Purchased together does not exist but viewed together exists
        # Case 4: Both Purchased together and Viewed together don't exist
        purchase_bundle = PurchaseBundle(
            item_id=item_id_pt,
            recommendations=["1", "2", "3", "4", "8"],
            score=[4, 6, 5, 7, 1],
        )
        viewed_together = ViewedTogether(
            item_id=item_id_vt,
            recommendations=["4", "5", "6", "7", "8"],
            score=[5, 7, 3, 4, 9],
        )
        purchase_bundle.save()
        viewed_together.save()
        response = client.get(
            f"/api/rec/michaels/purchased_and_viewed_together?item_id=15374&view_weight=5&candidate_count=6"
            f"&{filter_url_string}"
        )
        purchase_bundle.delete()
        viewed_together.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_purchased_and_viewed_together_bad_request(self):
        response = client.get("/api/rec/michaels/purchased_and_viewed_together")
        assert response.status_code == 400

    def test_viewed_together(self):
        viewed_together = ViewedTogether(
            item_id="435106",
            recommendations=["1", "2", "3"],
            score=[4, 6, 8],
        )
        viewed_together.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/viewed_together?item_id=435106&candidate_count=2"
            f"&{filter_url_string}"
        )
        viewed_together.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_viewed_together_empty(self):
        response = client.get(
            f"/api/rec/michaels/viewed_together?item_id=100&candidate_count=2"
            f"&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_viewed_together_bad_request(self):
        response = client.get("/api/rec/michaels/viewed_together")
        assert response.status_code == 400

    def test_add_user_defined_trending_now(self):
        expect = {
            "category_path": "root//Planners",
            "recommendations": ["462525", "57256", "562758", "52645"],
        }
        response = client.put(
            f"/api/rec/michaels/add_user_defined_trending_now?category_path=root%2F%2FPlanners&rec_item_ids=462525%2C57256"
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
            f"/api/rec/michaels/user_defined_trending_now?category_path={category_path}"
            f"&candidate_count=3&{filter_url_string}"
        )
        user_def_tn.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_user_defined_trending_now_404(self):
        response = client.get(
            f"/api/rec/michaels/user_defined_trending_now?category_path=root%2F%2FCustom%20Frames"
            f"&candidate_count=2&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_user_defined_trending_now_bad_request(self):
        response = client.get(
            "/api/rec/michaels/user_defined_trending_now?candidate_count=1"
        )
        assert response.status_code == 400

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
            f"/api/rec/michaels/trending_now_model?category_path={category_path}"
            f"&candidate_count=3&{filter_url_string}"
        )
        trending_now.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_trending_now_model_404(self):
        response = client.get(
            f"/api/rec/michaels/trending_now_model?category_path=root%2F%2FShopping%20Categories"
            f"&candidate_count=2&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_trending_now_model_bad_request(self):
        response = client.get("/api/rec/michaels/trending_now_model?candidate_count=1")
        assert response.status_code == 400

    def test_trending_now(self):
        mod_trending_now = TrendingNowModel(
            category_path="root//Shop Categories",
            recommendations=["4", "5", "6"],
        )
        user_def_tn = UserDefTrendingNow(
            category_path="root//Shop Categories",
            recommendations=["1", "2", "3"],
        )
        mod_trending_now.save()
        user_def_tn.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/trending_now?category_path=root%2F%2FShop%20Categories"
            f"&candidate_count=3&{filter_url_string}"
        )
        mod_trending_now.delete()
        user_def_tn.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_trending_now_all_category(self):
        local_conn1, local_col1 = create_local_connection(
            collection_name="mik_udf_tn_coll"
        )
        local_conn2, local_col2 = create_local_connection(collection_name="mik_tn_coll")
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
            f"/api/rec/michaels/trending_now_all_category?user_defined_trending_now=mik_udf_tn_coll"
            f"&trending_now=mik_tn_coll&candidate_count=2&{filter_url_string}"
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, json.loads(response.data))

    def test_featured_category(self):
        featured_category = FeaturedCategory(
            user_id=1001,
            recommendations=["root//Accessories//Barrettes", "root//Paint//Acrylic"],
            score=[2, 3],
        )
        featured_category.save()
        expect = ["root//Accessories//Barrettes", "root//Paint//Acrylic"]
        response = client.get("/api/rec/michaels/featured_category?user_id=1001")
        featured_category.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_buy_it_again(self):
        buy_it_again = BuyItAgain(
            user_id=302, recommendations=["3", "2", "1"], score=[2, 4, 6, 9]
        )
        buy_it_again.save()
        expect = ["2", "1"]
        response = client.get(
            f"/api/rec/michaels/buy_it_again?user_id=302&{filter_url_string}"
        )
        buy_it_again.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_buy_it_again_mpg(self):
        buy_it_again_mpg = BuyItAgainMPG(
            user_id=122, recommendations=["3", "2", "1"], score=[3, 5, 7]
        )
        buy_it_again_mpg.save()
        expect = ["2", "1"]
        response = client.get(
            f"/api/rec/michaels/buy_it_again_mpg?user_id=122&{filter_url_string}"
        )
        buy_it_again_mpg.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_search_keyword(self):
        popular_search_keyword = PopularSearchKeyword(
            group_id=0, recommendations=["Top", "Search", "Word"], score=[7, 6, 5]
        )
        popular_search_keyword.save()
        expect = ["Top", "Search", "Word"]
        response = client.get(
            f"/api/rec/michaels/popular_search_keyword?candidate_count=3"
        )
        popular_search_keyword.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_top_picks(self):
        # add fake top picks items
        redis_top_pics_hkey = michaels_args["top_picks_args"]["redis_hash_key"][
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
            f"/api/rec/michaels/top_picks?user_id=3759&candidate_count=3&{filter_url_string}"
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
        response = client.get(f"/api/rec/michaels/rec_for_you_search?user_id={user_id}")
        rec_for_you_search.delete()
        popular_search_keywords.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_rec_for_you_search_bad_request(self):
        response = client.get("/api/rec/michaels/rec_for_you_search?candidate_count=n")
        assert response.status_code == 400

    def test_people_also_buy(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="333", recommendations=["1", "2", "3"], score=[4, 5, 7]
        )
        people_also_buy.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/people_also_buy?item_id=333&candidate_count=3"
            f"&{filter_url_string}"
        )
        people_also_buy.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_people_also_view(self):
        people_also_view = PeopleAlsoView(
            item_id="333", recommendations=["1", "2", "3"], score=[4, 5, 7]
        )
        people_also_view.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/people_also_view?item_id=333&candidate_count=3"
            f"&{filter_url_string}"
        )
        people_also_view.delete()
        assert operator.eq(expect, json.loads(response.data))

    @pytest.mark.parametrize(
        "recommendations, expected",
        [
            (["1", "2", "3"], ["1", "2"]),
            ([], []),
        ],
    )
    def test_seasonal_top_picks(self, recommendations, expected):
        # Case 1: Recommendations exist
        # Case 2: Recommendations don't exist
        seasonal_top_picks = SeasonalTopPicks(
            group_id=0, recommendations=recommendations, score=[7, 6, 9]
        )
        seasonal_top_picks.save()
        response = client.get(
            f"/api/rec/michaels/seasonal_top_picks?candidate_count=3&{filter_url_string}"
        )
        seasonal_top_picks.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_seasonal_top_picks_bad_request(self):
        response = client.get("/api/rec/michaels/seasonal_top_picks?candidate_count")
        assert response.status_code == 400

    def test_project_use_this(self):
        project_use_this = ProjectUseThis(
            item_id="31", recommendations=["1", "2", "3"], score=[3, 4, 5]
        )
        project_use_this.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/project_use_this?item_id=31"
            f"&candidate_count=2&{project_filter_url_string}"
        )
        project_use_this.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_project_inspiration(self):
        project_inspiration = ProjectInspiration(
            user_id=12100005, recommendations=["4", "6", "8"], score=[5, 6, 7]
        )
        project_inspiration.save()
        expect = ["4", "8"]
        response = client.get(
            f"/api/rec/michaels/project_inspiration?user_id=12100005&candidate_count=2&{project_filter_url_string}"
        )
        project_inspiration.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_item(self):
        popular_item = PopularItem(
            group_id=0, recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        popular_item.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/popular_item?group_id=0&candidate_count=3&{filter_url_string}"
        )
        popular_item.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_similar_projects(self):
        project_similar = ProjectSimilarity(
            external_id="1083",
            recommendations=["1", "2", "3"],
            score=[5, 4, 7],
        )
        project_similar.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/similar_projects?external_id=1083&candidate_count=2&{project_filter_url_string}"
        )
        project_similar.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_similar_projects_404(self):
        response = client.get(
            "/api/rec/michaels/similar_projects?external_id=1110&candidate_count=2"
        )
        assert response.status_code == 404

    def test_similar_projects_bad_request(self):
        response = client.get("/api/rec/michaels/similar_projects?candidate_count=11")
        assert response.status_code == 400

    def test_popular_event(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        popular_event = PopularEvent(
            group_id=0, recommendations=["1", "2", "3"], score=[1, 2, 3]
        )
        popular_event.save()
        expect = ["1", "2", "3"]
        response = client.get(
            "/api/rec/michaels/popular_event?group_id=0&candidate_count=2&event_type=ONLINE"
        )
        popular_event.delete()
        assert operator.eq(expect, json.loads(response.data))

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
            "/api/rec/michaels/similar_events?event_id=103&candidate_count=3&event_type=ONLINE"
        )
        event_similar.delete()
        assert operator.eq(expect, json.loads(response.data))

    @pytest.mark.parametrize(
        "items_id_list, recommendations, score, expected",
        [
            (
                "item1 item2",
                ["1", "2", "3", "4"],
                [0.9, 0.8, 0.7, 0.6],
                ["1", "2", "4"],
            ),
            ("item1", ["1", "2", "3", "4"], [0.9, 0.9, 0.9, 0.9], ["1", "2", "4"]),
            ("item1", [None, None, None], [0.9, 0.9, 0.9], []),
            ("1001 1002", ["1", "2", "3", "4"], [1, 2, 3, 4], ["2", "1"]),
        ],
    )
    def test_similar_items_for_bundle(
        self, items_id_list, recommendations, score, expected, mongo_insert_items_list
    ):
        # Case 1: All items available in redis
        # Case 2: Items with same score in redis
        # Case 3: Items with None values in redis
        # Case 4: Get data from mongodb collection
        redis_similar_items_hkey = michaels_args["similar_items_args"][
            "redis_similar_items_hash_key"
        ]["default"]
        redis_client.hset(
            redis_similar_items_hkey,
            "item1",
            json.dumps(
                {
                    "recommendations": recommendations,
                    "score": score,
                }
            ),
        )
        redis_client.hset(
            redis_similar_items_hkey,
            "item2",
            json.dumps(
                {
                    "recommendations": ["item103", "item102", "item101", "item106"],
                    "score": [0.9, 0.8, 0.7, 0.6],
                }
            ),
        )
        response = client.get(
            f"/api/rec/michaels/similar_items_for_bundle?items_id_list={items_id_list}"
            f"&{similar_items_for_bundle_args_url_string}&{filter_url_string}"
        )
        redis_client.delete(redis_similar_items_hkey)
        assert operator.eq(expected, json.loads(response.data))

    def test_similar_items_for_bundle_404(self):
        response = client.get(
            f"/api/rec/michaels/similar_items_for_bundle?items_id_list=item1"
            f"&{similar_items_for_bundle_args_url_string}&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_similar_items_for_bundle_bad_request(self):
        response = client.get(
            f"/api/rec/michaels/similar_items_for_bundle?"
            f"{similar_items_for_bundle_args_url_string}&{filter_url_string}"
        )
        assert response.status_code == 400

    def test_event_for_you(
        self,
        mock_filter_no_schedule_events_in_mongo,
        mock_filter_archived_events_in_mongo,
    ):
        event_recommend = EventForYou(
            user_id=1999, recommendations=["1", "2", "3"], score=[1, 2, 3]
        )
        event_recommend.save()
        expect = ["1", "2", "3"]
        response = client.get(
            "/api/rec/michaels/event_for_you?user_id=1999&candidate_count=3&event_type=ONLINE"
        )
        event_recommend.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_category(self):
        popular_category = PopularCategory(
            group_id=0,
            recommendations=["root//AA", "root//BB", "root//CC"],
            score=[2, 5, 7],
        )
        popular_category.save()
        expect = ["root//AA", "root//BB"]
        response = client.get(
            "/api/rec/michaels/popular_category?group_id=0&candidate_count=2"
        )
        popular_category.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_project(self):
        popular_project = PopularProject(
            group_id=0, recommendations=["1", "2", "3"], score=[7, 8, 9]
        )
        popular_project.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/popular_project?candidate_count=2&{project_filter_url_string}"
        )
        popular_project.delete()
        assert operator.eq(expect, json.loads(response.data))

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
            f"/api/rec/michaels/search_people_also_buy?items_scores=2%203&items_id_list=101%20102"
            f"&candidate_count=3&collection_name=test_pab&{filter_url_string}"
        )
        assert operator.eq(expect, json.loads(response.data))

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
            f"/api/rec/michaels/search_people_also_buy?items_id_list=101%20102&candidate_count=3"
            f"&collection_name=test_pab&{filter_url_string}"
        )
        assert operator.eq(expect, json.loads(response.data))

    def test_search_rerank(self, redis_search_rerank):
        # The item vector in the redis is of size(1, 300) but here we are using size(1, 10) vector to test
        data = search_rerank_data[0]
        mimetype = "application/json"
        headers = {"Content-Type": mimetype, "Accept": mimetype}
        expect = {"1022": 0.4082482904638631, "1011": 0.22360679774997896}
        response = client.post(
            "/api/rec/michaels/search_rerank", data=json.dumps(data), headers=headers
        )
        assert operator.eq(expect, json.loads(response.data))

    # 404 cases
    def test_favorite_item_for_you_404(self):
        favorite_item_for_you = FavoriteItemForYou(
            user_id="125", recommendations=["1", "2", "3"], score=[7, 8, 9]
        )
        favorite_item_for_you.save()

        favorite_item = FavoriteItem(
            group_id=0, recommendations=["2", "3", "4"], score=[7, 8, 9]
        )
        favorite_item.save()

        expect = ["2", "4"]

        response = client.get(
            f"/api/rec/michaels/favorite_item_for_you?user_id=453&candidate_count=2"
            f"&{filter_url_string}"
        )

        favorite_item.delete()
        favorite_item_for_you.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_item_404(self):
        popular_item = PopularItem(
            group_id=1, recommendations=["100009", "100001"], score=[5, 6]
        )
        popular_item.save()
        response = client.get(
            f"/api/rec/michaels/popular_item/group_id=2&{filter_url_string}"
        )
        popular_item.delete()
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "redis_similar_items",
        ["mik_similar_items"],
        indirect=True,
    )
    def test_similar_items_404(self, redis_similar_items):
        response = client.get(
            f"/api/rec/b2b_edu/similar_items?item_id=102&candidate_count=2&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_purchased_together_404(self):
        purchase_bundle = PurchaseBundle(
            item_id="10062488", recommendations=["10371038", "10184631"], score=[7, 3]
        )
        purchase_bundle.save()
        response = client.get(
            f"/api/rec/michaels/purchased_together?item_id=100&candidate_count=2"
            f"&{filter_url_string}"
        )
        purchase_bundle.delete()
        assert json.loads(response.data) == []

    def test_add_user_defined_trending_now_404(self):
        # Case where list of recommendations is empty
        expect = {"category_path": "root//Planners", "recommendations": []}
        response = client.put(
            f"/api/rec/michaels/add_user_defined_trending_now?category_path=root%2F%2FPlanners"
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
            recommendations=["10546187", "10597055"],
        )
        trending_now.save()
        response = client.get(
            f"/api/rec/michaels/trending_now_model?category_path=root%2F%2FShopping%20Categories"
            f"&candidate_count=2&{filter_url_string}"
        )
        trending_now.delete()
        assert json.loads(response.data) == []

    def test_trending_now_all_category_404(self):
        local_conn1, local_col1 = create_local_connection(
            collection_name="mik_udf_tn_coll"
        )
        local_conn2, local_col2 = create_local_connection(collection_name="mik_tn_coll")
        response = client.get(
            f"/api/rec/michaels/trending_now_all_category?user_defined_trending_now=mik_udf_tn_coll"
            f"&trending_now=mik_tn_coll&{filter_url_string}"
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert json.loads(response.data) == []

    def test_featured_category_404(self):
        featured_category = FeaturedCategory(
            user_id=1002,
            recommendations=["root//Accessories//Barrettes", "root//Paint//Acrylic"],
            score=[4, 8],
        )
        popular_category = PopularCategory(
            group_id=0, recommendations=["DD", "EE", "FF"], score=[6, 7, 9]
        )
        featured_category.save()
        popular_category.save()
        response = client.get(
            "/api/rec/michaels/featured_category?user_id=2002&candidate_count=2"
        )
        expect = ["DD", "EE"]
        featured_category.delete()
        popular_category.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_buy_it_again_404(self):
        buy_it_again = BuyItAgain(
            user_id=12, recommendations=["1", "2", "3"], score=[9, 3, 8]
        )
        buy_it_again.save()
        expect = []
        response = client.get(
            f"/api/rec/michaels/buy_it_again?user_id=2011&{filter_url_string}"
        )
        buy_it_again.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_buy_it_again_mpg_404(self):
        buy_it_again_mpg = BuyItAgainMPG(
            user_id=32, recommendations=["3", "1", "7"], score=[3, 2, 1]
        )
        buy_it_again_mpg.save()
        expect = []
        response = client.get(
            f"/api/rec/michaels/buy_it_again_mpg?user_id=587&{filter_url_string}"
        )
        buy_it_again_mpg.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_search_keyword_404(self):
        response = client.get(
            f"/api/rec/michaels/popular_search_keyword?candidate_count=3"
        )
        assert response.status_code == 404

    def test_top_picks_404(self):
        response = client.get(
            f"/api/rec/michaels/top_picks?user_id=5678&candidate_count=3&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_people_also_buy_404(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="75", recommendations=["108", "131"], score=[5, 8]
        )
        people_also_buy.save()
        response = client.get(
            f"/api/rec/michaels/people_also_buy?item_id=3&candidate_count=2"
            f"&{filter_url_string}"
        )
        people_also_buy.delete()
        assert json.loads(response.data) == []

    def test_people_also_view_404(self):
        people_also_view = PeopleAlsoView(
            item_id="75", recommendations=["108", "131"], score=[5, 8]
        )
        people_also_view.save()
        response = client.get(
            f"/api/rec/michaels/people_also_view?item_id=3&candidate_count=2"
            f"&{filter_url_string}"
        )
        people_also_view.delete()
        assert json.loads(response.data) == []

    def test_project_use_this_404(self):
        project_use_this = ProjectUseThis(
            item_id="31", recommendations=["181", "312"], score=[1, 7]
        )
        project_use_this.save()
        response = client.get(
            "/api/rec/michaels/project_use_this?item_id=11&candidate_count=2"
        )
        project_use_this.delete()
        assert response.status_code == 404

    def test_project_inspiration_404(self):
        project_inspiration = ProjectInspiration(
            user_id=112, recommendations=["1", "2", "3"], score=[2, 4, 7]
        )
        popular_project = PopularProject(
            group_id=0, recommendations=["4", "6", "8"], score=[5, 6, 7]
        )
        project_inspiration.save()
        popular_project.save()
        expect = ["4", "8"]
        response = client.get(
            f"/api/rec/michaels/project_inspiration?user_id=211&candidate_count=2&{project_filter_url_string}"
        )
        project_inspiration.delete()
        popular_project.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_event_for_you_404(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        event_recommend = EventForYou(
            user_id=666, recommendations=["5001", "5002", "5003"], score=[5, 6, 7]
        )
        popular_event = PopularEvent(
            group_id=0, recommendations=["11", "12"], score=[1, 2]
        )
        event_recommend.save()
        popular_event.save()
        response = client.get(
            f"/api/rec/michaels/event_for_you?user_id=123&event_type=ONLINE&{filter_archive_url_string}"
        )
        expect = ["1", "2", "3"]
        popular_event.delete()
        event_recommend.delete()
        assert operator.eq(expect, json.loads(response.data))

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

    def test_similar_events_404(self):
        event_similar = SimilarEvents(
            event_id="10083", recommendations=["10622", "10585"], score=[9, 10]
        )
        event_similar.save()
        response = client.get(
            f"/api/rec/michaels/similar_events?event_id=10088&candidate_count=2&event_type=ONLINE"
        )
        event_similar.delete()
        assert response.status_code == 404

    def test_popular_project_404(self):
        popular_project = PopularProject(
            group_id=1, recommendations=["10109", "10101"], score=[5, 6]
        )
        popular_project.save()
        response = client.get("/api/rec/michaels/popular_project")
        popular_project.delete()
        assert response.status_code == 404

    def test_popular_category_404(self):
        popular_category = PopularCategory(
            group_id=1, recommendations=["root//GG", "root//JJ"], score=[1, 3, 4]
        )
        popular_category.save()
        response = client.get("/api/rec/michaels/popular_category?group_id=2")
        popular_category.delete()
        assert response.status_code == 404

    def test_search_people_also_buy_404(self):
        response = client.get(
            f"/api/rec/michaels/search_people_also_buy?items_scores=2%203&items_id_list=666%20999"
            f"&candidate_count=3&collection_name=test_col&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_search_rerank_404(self, redis_search_rerank):
        # The item vector in the redis is of size(1, 300) but here we are using size(1, 10) vector to test
        data = search_rerank_data[3]
        mimetype = "application/json"
        headers = {"Content-Type": mimetype, "Accept": mimetype}
        response = client.post(
            "/api/rec/michaels/search_rerank",
            data=json.dumps(data),
            headers=headers,
        )
        assert response.status_code == 404

    # Bad request cases
    def test_similar_items_bad_request(self):
        response = client.get("/api/rec/michaels/similar_items?candidate_count=1")
        assert response.status_code == 400

    def test_add_user_defined_trending_now_bad_request(self):
        response = client.put("/api/rec/michaels/add_user_defined_trending_now")
        assert response.status_code == 400

    def test_trending_now_bad_request(self):
        response = client.get("/api/rec/michaels/trending_now?candidate_count=1")
        assert response.status_code == 400

    def test_trending_now_all_category_bad_request(self):
        response = client.get(
            "/api/rec/michaels/trending_now_all_category?candidate_count=c"
        )
        assert response.status_code == 400

    def test_favorite_item_for_you_bad_request(self):
        response = client.get(
            "/api/rec/michaels/favorite_item_for_you?candidate_count=3"
        )
        assert response.status_code == 400

    def test_purchased_together_bad_request(self):
        response = client.get("/api/rec/michaels/purchased_together")
        assert response.status_code == 400

    def test_featured_category_bad_request(self):
        response = client.get("/api/rec/michaels/featured_category")
        assert response.status_code == 400

    def test_buy_it_again_bad_request(self):
        response = client.get("/api/rec/michaels/buy_it_again?candidate_count=6")
        assert response.status_code == 400

    def test_buy_it_again_mpg_bad_request(self):
        response = client.get("/api/rec/michaels/buy_it_again_mpg?candidate_count=6")
        assert response.status_code == 400

    def test_popular_search_keyword_bad_request(self):
        response = client.get(
            f"/api/rec/michaels/popular_search_keyword?candidate_count=h"
        )
        assert response.status_code == 400

    def test_top_picks_bad_request(self):
        response = client.get(f"/api/rec/michaels/top_picks")
        assert response.status_code == 400

    def test_people_also_buy_bad_request(self):
        response = client.get("/api/rec/michaels/people_also_buy?candidate_count=3")
        assert response.status_code == 400

    def test_people_also_view_bad_request(self):
        response = client.get("/api/rec/michaels/people_also_view?candidate_count=3")
        assert response.status_code == 400

    def test_project_use_this_bad_request(self):
        response = client.get("/api/rec/michaels/project_use_this?candidate_count")
        assert response.status_code == 400

    def test_project_inspiration_bad_request(self):
        response = client.get("/api/rec/michaels/project_inspiration?user_id")
        assert response.status_code == 400

    def test_popular_item_bad_request(self):
        response = client.get("/api/rec/michaels/popular_item?candidate_count=None")
        assert response.status_code == 400

    def test_similar_events_bad_request(self):
        response = client.get("/api/rec/michaels/similar_events?candidate_count=11")
        assert response.status_code == 400

    def test_event_for_you_bad_request(self):
        response = client.get("/api/rec/michaels/event_for_you?candidate_count=1")
        assert response.status_code == 400

    def test_popular_event_bad_request(self):
        response = client.get("/api/rec/michaels/popular_event?candidate_count=None")
        assert response.status_code == 400

    def test_popular_category_bad_request(self):
        response = client.get("/api/rec/michaels/popular_category?candidate_count=None")
        assert response.status_code == 400

    def test_popular_project_bad_request(self):
        response = client.get("/api/rec/michaels/popular_project?candidate_count=None")
        assert response.status_code == 400

    def test_search_people_also_buy_bad_request(self):
        response = client.get(
            "/api/rec/michaels/search_people_also_buy?candidate_count=8"
        )
        assert response.status_code == 400

    def test_search_rerank_bad_request(self):
        response = client.post("/api/rec/michaels/search_rerank")
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
            f"/api/rec/michaels/recently_viewed_streaming?user_id=mik_streaming_recently_view_123"
            f"&candidate_count=4&{filter_url_string}"
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
            f"/api/rec/michaels/recently_viewed_streaming?user_id=mik_streaming_recently_view_123"
            f"&candidate_count=3&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_recently_viewed_streaming_bad_request(self):
        response = client.get(
            "/api/rec/michaels/recently_viewed_streaming?candidate_count=3"
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
            f"/api/rec/michaels/you_may_also_buy?user_id={user_id}&candidate_count=3"
            f"&{filter_url_string}"
        )
        you_may_also_buy.delete()
        popular_item.delete()
        assert operator.eq(expected, json.loads(response.data))

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
            f"/api/rec/michaels/popular_item_by_category?category_path={category_path}&candidate_count=2"
            f"&{filter_url_string}"
        )
        popular_item_by_category.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_popular_item_by_category_bad_request(self):
        response = client.get(
            "/api/rec/michaels/popular_item_by_category?candidate_count=3"
        )
        assert response.status_code == 400

    def test_you_may_also_buy_bad_request(self):
        response = client.get("/api/rec/michaels/you_may_also_buy?candidate_count=3")
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "group_id, expected",
        [
            (0, ["1", "2"]),
            (1, []),
        ],
    )
    def test_michaels_trending_project(self, group_id, expected):
        # Case 1: when recommendations exist
        # Case 2: when no recommendations exist
        trending_project = TrendingProject(
            group_id=group_id, recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        trending_project.save()
        response = client.get(
            f"/api/rec/michaels/trending_project?candidate_count=2"
            f"&{project_filter_url_string}"
        )
        trending_project.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_michaels_trending_project_bad_request(self):
        response = client.get("/api/rec/michaels/trending_project?candidate_count=None")
        assert response.status_code == 400

    def test_michaels_popular_item_by_store(self):
        popular_item_by_store = PopularItemByStore(
            store_id=777, recommendations=["8", "7", "6"], score=[8, 7, 6]
        )
        popular_item_by_store.save()
        expect = ["8", "7"]
        response = client.get(
            f"/api/rec/michaels/popular_item_by_store?store_id=777&candidate_count=2"
            f"&{filter_url_string}"
        )
        popular_item_by_store.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_michaels_popular_item_by_store_404(self):
        response = client.get(
            f"/api/rec/michaels/popular_item_by_store?store_id=777&candidate_count=2"
            f"&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_michaels_popular_item_by_store_bad_request(self):
        response = client.get(
            f"/api/rec/michaels/popular_item_by_store?candidate_count=None"
            f"&{filter_url_string}"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "items_id_list, expected",
        [
            ("1001 1002 1003", ["2", "1"]),
            ("1004", []),
        ],
    )
    def test_purchased_together_bundle(
        self, mongo_insert_items_list, items_id_list, expected
    ):
        # Case 1: With valid item_id_list
        # Case 2: Without valid item_list
        collection_name = "test_collection"
        response = client.get(
            f"/api/rec/michaels/purchased_together_bundle?items_id_list={items_id_list}"
            f"&candidate_count=3&{filter_url_string}&collection_name={collection_name}"
        )
        assert operator.eq(expected, json.loads(response.data))

    def test_purchased_together_bundle_bad_request(self):
        response = client.get(
            "/api/rec/michaels/purchased_together_bundle?candidate_count=3"
        )
        assert response.status_code == 400

    def test_michaels_popular_products_in_projects(self):
        popular_products_in_projects = PopularProductsInProjects(
            group_id=0, recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        popular_products_in_projects.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/popular_products_in_projects?candidate_count=3"
            f"&{filter_url_string}"
        )
        popular_products_in_projects.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_michaels_popular_products_in_projects_404(self):
        response = client.get(
            f"/api/rec/michaels/popular_products_in_projects?candidate_count=2"
            f"&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_michaels_popular_products_in_projects_bad_request(self):
        response = client.get(
            "/api/rec/michaels/popular_products_in_projects?candidate_count"
        )
        assert response.status_code == 400

    def test_yesterday_popular_item(self):
        yesterday_popular_item = YesterdayPopularItem(
            group_id=0, recommendations=["2", "4", "6", "8"], score=[7, 6, 5, 4]
        )
        yesterday_popular_item.save()
        expect = ["2", "4", "8"]
        response = client.get(
            f"/api/rec/michaels/yesterday_popular_item?{filter_url_string}"
        )
        yesterday_popular_item.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_yesterday_popular_item_404(self):
        response = client.get(
            f"/api/rec/michaels/yesterday_popular_item?{filter_url_string}"
        )
        assert response.status_code == 404

    def test_yesterday_popular_item_bad_request(self):
        response = client.get(
            "/api/rec/michaels/yesterday_popular_item?candidate_count"
        )
        assert response.status_code == 400

    def test_michaels_new_projects(self):
        new_projects = NewProjects(group_id=0, recommendations=["1", "2", "3"])
        new_projects.save()

        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/new_projects?candidate_count=2&{project_filter_url_string}"
        )
        new_projects.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_michaels_new_projects_404(self):
        response = client.get("/api/rec/michaels/new_projects?candidate_count=2")
        assert response.status_code == 404

    def test_michaels_new_projects_bad_request(self):
        response = client.get("/api/rec/michaels/new_projects?candidate_count")
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
            "/api/rec/michaels/upcoming_event?candidate_count=3&event_type=ONLINE"
        )
        upcoming_event.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_michaels_upcoming_event_404(self):
        response = client.get(
            "/api/rec/michaels/upcoming_event?candidate_count=2&event_type=ONLINE"
        )
        assert response.status_code == 404

    def test_michaels_upcoming_event_bad_request(self):
        response = client.get("/api/rec/michaels/upcoming_event?candidate_count")
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
            "/api/rec/michaels/trending_event?group_id=0&candidate_count=3&event_type=ONLINE"
        )
        trending_event.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_trending_event_404(self):
        response = client.get(
            "/api/rec/michaels/trending_event?group_id=12&event_type=ONLINE"
        )
        assert response.status_code == 404

    def test_trending_event_bad_request(self):
        response = client.get("/api/rec/michaels/trending_event?candidate_count=None")
        assert response.status_code == 400

    def test_popular_clearance_category(self):
        popular_clearance_category = PopularClearanceCategory(
            group_id=0,
            recommendations=["root//AA", "root//BB", "root//CC"],
            score=[12, 5, 1],
        )
        popular_clearance_category.save()
        expect = ["root//AA", "root//BB"]
        response = client.get(
            "/api/rec/michaels/popular_clearance_category?candidate_count=2"
        )
        popular_clearance_category.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_clearance_category_404(self):
        response = client.get("/api/rec/michaels/popular_clearance_category")
        assert response.status_code == 404

    def test_popular_clearance_category_bad_request(self):
        response = client.get(
            "/api/rec/michaels/popular_clearance_category?candidate_count="
        )
        assert response.status_code == 400

    def test_popular_sale_category(self):
        popular_sale_category = PopularSaleCategory(
            group_id=0,
            recommendations=["root//ABC", "root//DEF", "root//GHI"],
            score=[12, 5, 1],
        )
        popular_sale_category.save()
        expect = ["root//ABC", "root//DEF"]
        response = client.get(
            f"/api/rec/michaels/popular_sale_category?candidate_count=2"
            f"&{filter_url_string}"
        )
        popular_sale_category.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_sale_category_404(self):
        response = client.get(
            f"/api/rec/michaels/popular_sale_category&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_popular_sale_category_bad_request(self):
        response = client.get(
            f"/api/rec/michaels/popular_sale_category?candidate_count="
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            ("user1", ["item101", "item103"]),
            ("", ["item101", "item103"]),
        ],
    )
    def test_popular_clearance_item(
        self, mongo_filter_item_with_badge, user_id, expected
    ):
        # Case 1: With user id
        # Case 2: Without user id
        redis_popular_clearance_item_hash_key = michaels_args[
            "popular_clearance_item_args"
        ]["redis_popular_clearance_item_hash_key"]["default"]
        redis_client.hset(
            redis_popular_clearance_item_hash_key,
            "user1",
            json.dumps(
                {
                    "recommendations": ["item101", "item102", "item103"],
                    "score": [0.9, 0.8, 0.5],
                }
            ),
        )
        popular_clearance_item = PopularClearanceItem(
            group_id=0,
            recommendations=["item101", "item102", "item103"],
            score=[11, 33, 54],
        )
        popular_clearance_item.save()
        response = client.get(
            f"/api/rec/michaels/popular_clearance_item?user_id={user_id}&candidate_count=2"
            f"&{filter_url_string}&{filter_badges_url_string}"
        )
        popular_clearance_item.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_popular_clearance_item_404(self):
        response = client.get(
            f"/api/rec/michaels/popular_clearance_item?candidate_count=2"
            f"&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_popular_clearance_item_bad_request(self):
        response = client.get(
            "/api/rec/michaels/popular_clearance_item?candidate_count=None"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            ("user1", ["item101", "item103"]),
            ("", ["item101", "item103"]),
        ],
    )
    def test_popular_sale_item(self, mongo_filter_item_with_badge, user_id, expected):
        # Case 1: With user id
        # Case 2: Without user id
        redis_popular_sale_item_hash_key = michaels_args["popular_sale_item_args"][
            "redis_popular_sale_item_hash_key"
        ]["default"]
        redis_client.hset(
            redis_popular_sale_item_hash_key,
            "user1",
            json.dumps(
                {
                    "recommendations": ["item101", "item102", "item103"],
                    "score": [0.9, 0.8, 0.5],
                }
            ),
        )
        popular_sale_item = PopularSaleItem(
            group_id=0,
            recommendations=["item101", "item102", "item103"],
            score=[11, 33, 54],
        )
        popular_sale_item.save()
        response = client.get(
            f"/api/rec/michaels/popular_sale_item?user_id={user_id}&candidate_count=2"
            f"&{filter_url_string}&{filter_badges_url_string}"
        )
        popular_sale_item.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_popular_sale_item_404(self):
        response = client.get(
            f"/api/rec/michaels/popular_sale_item?candidate_count=2"
            f"&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_popular_sale_item_bad_request(self):
        response = client.get(
            "/api/rec/michaels/popular_sale_item?candidate_count=None"
        )
        assert response.status_code == 400

    def test_popular_visited_events(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        popular_visited_events = PopularVisitedEvents(
            group_id=0,
            recommendations=["1", "2", "3"],
            score=[12, 5, 1],
        )
        popular_visited_events.save()
        expect = ["1", "2", "3"]
        response = client.get(
            "/api/rec/michaels/popular_visited_events?candidate_count=2&event_type=ONLINE"
        )
        popular_visited_events.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_visited_events_404(self):
        response = client.get(
            "/api/rec/michaels/popular_visited_events&event_type=ONLINE"
        )
        assert response.status_code == 404

    def test_popular_visited_events_bad_request(self):
        response = client.get(
            "/api/rec/michaels/popular_visited_events?candidate_count="
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
            "/api/rec/michaels/popular_first_layer_category?candidate_count=2"
        )
        popular_first_layer_category.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_first_layer_category_404(self):
        response = client.get("/api/rec/michaels/popular_first_layer_category")
        assert response.status_code == 404

    def test_popular_first_layer_category_bad_request(self):
        response = client.get(
            "/api/rec/michaels/popular_first_layer_category?candidate_count="
        )
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
            "/api/rec/michaels/popular_visited_projects?candidate_count=2"
        )
        popular_visited_projects.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_visited_projects_404(self):
        response = client.get("/api/rec/michaels/popular_visited_projects")
        assert response.status_code == 404

    def test_popular_visited_projects_bad_request(self):
        response = client.get(
            "/api/rec/michaels/popular_visited_projects?candidate_count="
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
            "/api/rec/michaels/popular_visited_items?candidate_count=2"
        )
        popular_visited_items.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_visited_items_404(self):
        response = client.get("/api/rec/michaels/popular_visited_items")
        assert response.status_code == 404

    def test_popular_visited_items_bad_request(self):
        response = client.get(
            "/api/rec/michaels/popular_visited_items?candidate_count="
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "mongo_filter_scored_item_with_collection_name",
        ["mik_purchased_together"],
        indirect=True,
    )
    def test_shopping_cart_bundle(self, mongo_filter_scored_item_with_collection_name):
        expect = ["2", "1"]
        response = client.get(
            f"/api/rec/michaels/shopping_cart_bundle?items_id_list=103%20104%20105&candidate_count=4"
            f"&{filter_url_string}"
        )
        assert operator.eq(expect, json.loads(response.data))

    def test_shopping_cart_bundle_404(self):
        expect = []
        response = client.get(
            "/api/rec/michaels/shopping_cart_bundle?items_id_list=1001&candidate_count=4"
        )
        assert operator.eq(expect, json.loads(response.data))

    def test_shopping_cart_bundle_bad_request(self):
        response = client.get("/api/rec/michaels/shopping_cart_bundle?candidate_count=")
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "item_id, expected",
        [
            ("456", ["1", "4"]),
            ("455", []),
        ],
    )
    def test_similar_items_in_same_store(self, item_id, expected):
        # Case 1: item exists in mongodb
        # Case 2: item doesn't exists
        similar_items_in_same_store = SimilarItemsInSameStore(
            item_id=item_id, recommendations=["1", "4", "7"], score=[6, 1, 9]
        )
        similar_items_in_same_store.save()
        response = client.get(
            f"/api/rec/michaels/similar_items_in_same_store?item_id=456&candidate_count=2"
            f"&{filter_url_string}"
        )
        similar_items_in_same_store.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_similar_items_in_same_store_bad_request(self):
        response = client.get(
            "/api/rec/michaels/similar_items_in_same_store?candidate_count=3"
        )
        assert response.status_code == 400

    def test_michaels_popular_products_in_events(self):
        popular_products_in_events = PopularProductsInEvents(
            group_id=0, recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        popular_products_in_events.save()

        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/michaels/popular_products_in_events?candidate_count=3"
            f"&{filter_url_string}"
        )
        popular_products_in_events.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_michaels_popular_products_in_events_404(self):
        response = client.get(
            f"/api/rec/michaels/popular_products_in_events?candidate_count=2"
            f"&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_michaels_popular_products_in_events_bad_request(self):
        response = client.get(
            "/api/rec/michaels/popular_products_in_events?candidate_count"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "mongo_related_category",
        ["test_sch"],
        indirect=True,
    )
    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("category_input", {"category1": "image1", "category2": "image2"}),
            ("invalid_category_input", []),
        ],
    )
    def test_michaels_related_categories_by_category(
        self, category_path, expected, mongo_related_category
    ):
        related_categories_by_category = RelatedCategoriesByCategory(
            category_path="category_input",
            recommendations=[
                "root//shop//t1//t2//category1",
                "root//shop//t1//t2//category2",
                "root//shop//t1//t2//category3",
            ],
        )
        related_categories_by_category.save()
        response = client.get(
            f"/api/rec/michaels/related_categories_by_category?category_path={category_path}"
            f"&candidate_count=2&collection_name=test_sch"
        )
        related_categories_by_category.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_michaels_related_categories_by_category_bad_request(self):
        response = client.get(
            "/api/rec/michaels/related_categories_by_category?candidate_count"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("category_input", ["query1", "query2"]),
            ("invalid_category_input", []),
        ],
    )
    def test_michaels_related_queries_by_category(self, category_path, expected):
        related_queries_by_category = RelatedQueriesByCategory(
            category_path="category_input",
            recommendations=["query1", "query2", "query3"],
        )
        related_queries_by_category.save()
        response = client.get(
            f"/api/rec/michaels/related_queries_by_category?category_path={category_path}"
            f"&candidate_count=2"
        )
        related_queries_by_category.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_michaels_related_queries_by_category_bad_request(self):
        response = client.get(
            "/api/rec/michaels/related_queries_by_category?candidate_count"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "mongo_similar_items_by_popularity",
        ["mik_popular_master_items"],
        indirect=True,
    )
    def test_michaels_similar_items_by_popularity(
        self, mongo_similar_items_by_popularity
    ):
        collection_name = "mik_popular_master_items"
        redis_similar_items_hkey = michaels_args["similar_items_args"][
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
            f"/api/rec/michaels/similar_items_by_popularity?candidate_count=5"
            f"&item_id=item1&collection_name={collection_name}&{filter_url_string}"
        )
        redis_client.delete(redis_similar_items_hkey)
        assert operator.eq(expected, json.loads(response.data))

    def test_michaels_similar_items_by_popularity_not_found(self):
        collection_name = "mik_popular_master_items"
        expected = []
        response = client.get(
            f"/api/rec/michaels/similar_items_by_popularity?candidate_count=2"
            f"&item_id=item1&collection_name={collection_name}&{filter_url_string}"
        )
        assert operator.eq(expected, json.loads(response.data))

    def test_michaels_similar_items_by_popularity_bad_request(self):
        response = client.get(
            "/api/rec/michaels/similar_items_by_popularity?candidate_count"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "query_keyword, expected",
        [("query_input", ["1", "2", "3"]), ("invalid_query_input", [])],
    )
    def test_michaels_related_queries_by_query(self, query_keyword, expected):
        related_queries = RelatedQueriesByQuery(
            query="query_input", recommendations=["1", "2", "3"], score=[7, 6, 5]
        )

        related_queries.save()
        response = client.get(
            f"/api/rec/michaels/related_queries_by_query?candidate_count=3&query_keyword={query_keyword}"
        )
        related_queries.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_michaels_related_queries_by_query_bad_request(self):
        response = client.get("/api/rec/michaels/related_queries_by_query")
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "mongo_related_category",
        ["test_sch"],
        indirect=True,
    )
    @pytest.mark.parametrize(
        "query_keyword, expected",
        [
            ("query_keyword", {"category1": "image1", "category2": "image2"}),
            ("invalid_query_keyword", []),
        ],
    )
    def test_michaels_related_categories_by_query(
        self, query_keyword, expected, mongo_related_category
    ):
        related_categories_by_query = RelatedCategoriesByQuery(
            query="query_keyword",
            recommendations=[
                "root//shop//t1//t2//category1",
                "root//shop//t1//t2//category2",
                "root//shop//t1//t2//category3",
            ],
            score=[1, 2, 3],
        )
        related_categories_by_query.save()
        response = client.get(
            f"/api/rec/michaels/related_categories_by_query?query_keyword={query_keyword}"
            f"&candidate_count=2&collection_name=test_sch"
        )
        related_categories_by_query.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_michaels_related_categories_by_query_bad_request(self):
        response = client.get(
            "/api/rec/michaels/related_categories_by_query?candidate_count"
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "mongo_filter_inactive_item_with_collection_name, mongo_filter_inactive_category",
        [(test_pfe, test_pfe)],
        indirect=True,
    )
    class TestMichaelsPicksFromExpectsController:
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
                f"/api/rec/michaels/picks_from_experts?user_id=169&category_count=2&candidate_count=2"
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
                f"/api/rec/michaels/picks_from_experts?category_count=2"
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
                "/api/rec/michaels/picks_from_experts?candidate_count=v"
            )
            assert response.status_code == 400


if __name__ == "__main__":
    pytest.main()
