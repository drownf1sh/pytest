import json
import operator
import pickle
import pytest
import time
from mongoengine import DoesNotExist

from app.main.model.michaels import (
    BuyItAgain,
    BuyItAgainMPG,
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
    PopularSaleCategory,
    PopularClearanceCategory,
    PopularClearanceItem,
    PopularSaleItem,
    PopularVisitedEvents,
    FavoriteItem,
    PopularVisitedProjects,
    PopularVisitedItems,
    ItemSimilarity,
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
from app.main.model.michaels import EventForYou
from app.main.model.michaels import FeaturedCategory
from app.main.model.michaels import PeopleAlsoBuy
from app.main.model.michaels import PeopleAlsoView
from app.main.model.michaels import PopularCategory
from app.main.model.michaels import PopularEvent
from app.main.model.michaels import PopularItem
from app.main.model.michaels import PopularProject
from app.main.model.michaels import ProjectInspiration
from app.main.model.michaels import ProjectSimilarity
from app.main.model.michaels import ProjectUseThis
from app.main.model.michaels import PurchaseBundle
from app.main.model.michaels import SeasonalTopPicks
from app.main.model.michaels import SimilarEvents
from app.main.model.michaels import UserRecommend
from app.main.service.michaels_service import (
    get_michaels_buy_it_again,
    get_michaels_buy_it_again_mpg,
    post_michaels_search_rerank,
    get_michaels_trending_now_model,
    get_michaels_user_defined_trending_now,
    put_michaels_user_defined_trending_now,
    get_michaels_trending_now_all_category,
    get_michaels_picks_from_experts,
    get_michaels_popular_search_keyword,
    get_michaels_you_may_also_buy,
    get_michaels_popular_item_by_store,
    get_michaels_purchased_together_bundle,
    get_michaels_popular_products_in_projects,
    get_michaels_top_picks,
    get_michaels_yesterday_popular_item,
    get_michaels_new_projects,
    get_michaels_similar_ad_items,
    get_michaels_upcoming_event,
    get_michaels_favorite_item_for_you,
    get_michaels_trending_event,
    get_michaels_popular_clearance_category,
    get_michaels_popular_sale_category,
    get_michaels_popular_clearance_item,
    get_michaels_popular_sale_item,
    get_michaels_popular_visited_events,
    get_michaels_streaming_trending_now_list,
    get_michaels_popular_first_layer_category,
    get_michaels_popular_visited_projects,
    get_michaels_popular_visited_items,
    get_michaels_shopping_cart_bundle,
    get_michaels_similar_items_in_same_store,
    get_michaels_popular_products_in_events,
    get_michaels_related_categories_by_category,
    get_michaels_similar_items_by_popularity,
    get_michaels_related_queries_by_query,
    get_michaels_related_categories_by_query,
    get_michaels_trending_project,
    get_michaels_popular_item_by_category,
    get_michaels_viewed_together,
    get_michaels_purchased_and_viewed_together,
)
from app.main.model.michaels import RecForYouSearch
from app.main.service.michaels_service import get_michaels_event_for_you
from app.main.service.michaels_service import get_michaels_featured_category
from app.main.service.michaels_service import get_michaels_people_also_buy
from app.main.service.michaels_service import get_michaels_people_also_view
from app.main.service.michaels_service import get_michaels_popular_category
from app.main.service.michaels_service import get_michaels_popular_event
from app.main.service.michaels_service import get_michaels_popular_item
from app.main.service.michaels_service import get_michaels_popular_project
from app.main.service.michaels_service import get_michaels_project_inspiration
from app.main.service.michaels_service import get_michaels_project_use_this
from app.main.service.michaels_service import get_michaels_purchased_together

from app.main.service.michaels_service import get_michaels_recently_viewed_streaming
from app.main.service.michaels_service import get_michaels_recommended_for_you
from app.main.service.michaels_service import get_michaels_seasonal_top_picks
from app.main.service.michaels_service import get_michaels_similar_events
from app.main.service.michaels_service import get_michaels_similar_items
from app.main.service.michaels_service import get_michaels_similar_items_for_bundle
from app.main.service.michaels_service import get_michaels_similar_projects
from app.main.service.michaels_service import get_michaels_trending_now
from app.main.service.michaels_service import get_michaels_search_people_also_buy
from app.main.service.michaels_service import get_michaels_rec_for_you_search
from app.main.service.michaels_service import get_michaels_related_queries_by_category
from app.main.util.exception_handler import NotEnoughRecommendations
from app.main.util.test_connection import create_local_connection
from app.main.util.test_connection import disconnect_local_connection
from app.main.util.global_db_connection import redis_client
from app.main.util.controller_args import michaels_args
from app.main.util.global_vars import ad_items_status_redis_hkey


# global var defined in conftest.py pytest_configure
filter_args = pytest.filter_args
test_pfe = pytest.test_pfe
test_tp = pytest.test_tp
project_filter_args = pytest.project_filter_args
recently_view_redis_data = pytest.recently_view_redis_data
test_pab = pytest.test_pab
search_rerank_data = pytest.search_rerank_data


class TestMichaelsService:
    filter_badges_args = {
        "badges_name": "badges",
        "badges_check_name": "badges_check_name",
        "badges_check_val": True,
        "badges_start_date_name": "badges_start_date_name",
        "badges_expiration_date_name": "badges_expiration_date_name",
    }

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
        ["mik_similar_items"],
        indirect=True,
    )
    def test_get_michaels_similar_items_service(
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
        result = get_michaels_similar_items(
            item_id=item,
            candidate_count=2,
            redis_similar_items_hash_key="mik_similar_items",
            similar_items_api=True,
            **filter_args,
        )

        assert operator.eq(expected, result)

    def test_get_michaels_similar_ad_items_service(self):
        # add fake ad items
        redis_similar_ad_items_hkey = michaels_args["similar_ad_items_args"][
            "redis_similar_ad_items_hash_key"
        ]["default"]
        redis_client.hset(
            redis_similar_ad_items_hkey,
            "item1",
            json.dumps({"recommendations": ["1", "2"], "score": [0.9, 0.8]}),
        )
        # add fake ad items' status
        redis_client.hset(ad_items_status_redis_hkey, "1", "1".encode("utf-8"))
        redis_client.hset(ad_items_status_redis_hkey, "2", "0".encode("utf-8"))

        result = get_michaels_similar_ad_items(
            item_id="item1",
            ad_candidate_count=2,
            redis_similar_ad_items_hash_key="mik_similar_ad_items",
            similar_items_api=False,
            **filter_args,
        )
        redis_client.delete(redis_similar_ad_items_hkey, ad_items_status_redis_hkey)
        assert result[0]["skuNumber"] == "1"
        assert result[0]["adsId"]

    def test_get_michaels_similar_ad_items_service_failed(self):
        # add fake ad items
        redis_similar_ad_items_hkey = michaels_args["similar_ad_items_args"][
            "redis_similar_ad_items_hash_key"
        ]["default"]
        redis_client.hset(
            redis_similar_ad_items_hkey,
            "item1",
            pickle.dumps(
                {"recommendations": ["item101_ad", "item102_ad"], "score": [0.9, 0.8]}
            ),
        )
        # add fake ad items' status
        redis_client.hset(ad_items_status_redis_hkey, "item101_ad", "1".encode("utf-8"))
        redis_client.hset(ad_items_status_redis_hkey, "item102_ad", "0".encode("utf-8"))

        try:
            get_michaels_similar_ad_items(
                item_id="item2",
                ad_candidate_count=2,
                redis_similar_ad_items_hash_key="mik_similar_ad_items",
                similar_items_api=False,
                **filter_args,
            )
        except DoesNotExist:
            assert True
        else:
            assert False
        redis_client.delete(redis_similar_ad_items_hkey, ad_items_status_redis_hkey)

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            (321, ["2", "1"]),
            (111, ["7", "8", "9"]),
        ],
    )
    def test_get_michaels_recommended_for_you_service_case_one_two(
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
        results = get_michaels_recommended_for_you(
            user_id=user_id, candidate_count=3, **filter_args
        )
        user_recommend.delete()
        popular_item.delete()
        assert operator.eq(expected, results)

    def test_get_michaels_recommended_for_you_service_case_three(self):
        # Case 3: recommend_for_you object, popular_item object do not exist
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_recommended_for_you(
                user_id=543, candidate_count=3, **filter_args
            )
        assert str(excinfo.value) == "PopularItem matching query does not exist."

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
        output = get_michaels_trending_project(candidate_count=2, **project_filter_args)
        trending_project.delete()
        assert operator.eq(expected, output)

    def test_get_michaels_event_for_you_service(
        self,
        mock_filter_no_schedule_events_in_mongo,
        mock_filter_archived_events_in_mongo,
    ):
        event_recommend = EventForYou(
            user_id=1321, recommendations=["1", "2", "3"], score=[1, 4, 7]
        )
        event_recommend.save()
        expect = ["1", "2", "3"]
        results = get_michaels_event_for_you(
            user_id=1321,
            candidate_count=3,
            spanner_table_name="test_events",
            event_type="ONLINE",
        )
        event_recommend.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_event_for_you_service_404(
        self,
        mock_filter_no_schedule_events_in_mongo,
        mock_filter_archived_events_in_mongo,
    ):
        event_recommend = EventForYou(
            user_id=3222, recommendations=["32", "22", "12"], score=[1, 4, 7]
        )
        popular_event = PopularEvent(
            group_id=0, recommendations=["1", "2", "3"], score=[1, 2]
        )
        event_recommend.save()
        popular_event.save()
        expect = ["1", "2", "3"]
        results = get_michaels_event_for_you(
            user_id=111,
            candidate_count=3,
            spanner_table_name="test_events",
            event_type="ONLINE",
        )
        popular_event.delete()
        event_recommend.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_top_picks_service_case_one(self):
        # Data exists in redis
        # add fake top picks items
        redis_top_picks_hkey = michaels_args["top_picks_args"]["redis_hash_key"][
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
        result = get_michaels_top_picks(
            user_id="3759",
            candidate_count=3,
            redis_hash_key="mik_streaming_top_picks",
            collection_name="mik_popular_item_by_category",
            **filter_args,
        )
        redis_client.delete(redis_top_picks_hkey)
        assert operator.eq(expect, result)

    @pytest.mark.parametrize(
        "mongo_filter_inactive_category",
        [test_tp],
        indirect=True,
    )
    def test_get_michaels_top_picks_service_case_two(
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
        result = get_michaels_top_picks(
            user_id="5599",
            candidate_count=3,
            redis_hash_key="mik_streaming_top_picks",
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
    def test_get_michaels_top_picks_service_case_three(
        self, mongo_filter_inactive_category
    ):
        # Not enough recommendations
        popular_first_layer_category = PopularFirstLayerCategory(
            group_id=0,
            recommendations=["root//ABC", "root//DEF", "root//GHI"],
            score=[7, 5, 4],
        )
        popular_first_layer_category.save()
        with pytest.raises(NotEnoughRecommendations) as excinfo:
            get_michaels_top_picks(
                user_id="3569",
                candidate_count=3,
                redis_hash_key="mik_streaming_top_picks",
                collection_name=test_tp,
                **filter_args,
            )
        popular_first_layer_category.delete()
        assert str(excinfo.value.detail) == "Not enough recommendations"

    def test_get_michaels_top_picks_service_case_four(self):
        # no recommendations
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_top_picks(
                user_id="5678",
                candidate_count=3,
                redis_hash_key="mik_streaming_top_picks",
                collection_name=test_tp,
                **filter_args,
            )
        assert (
            str(excinfo.value)
            == "PopularFirstLayerCategory matching query does not exist."
        )

    @pytest.mark.parametrize(
        "user_id, expect",
        [
            ("358", ["1", "2", "4"]),
            ("458", ["1", "2"]),
        ],
    )
    def test_get_michaels_favorite_item_for_you_service(self, user_id, expect):
        # Case 1: get recommendations from favorite_item_for_you
        # Case 2: get recommendations from favorite_item when favorite_item_for_you not exist
        favorite_item_for_you = FavoriteItemForYou(
            user_id="358",
            recommendations=["1", "2", "3", "4"],
            score=[1, 4, 6, 7],
        )
        favorite_item_for_you.save()
        favorite_item = FavoriteItem(
            group_id=0, recommendations=["1", "2", "3"], score=[7, 8, 9]
        )
        favorite_item.save()
        results = get_michaels_favorite_item_for_you(
            user_id=user_id, candidate_count=3, **filter_args
        )
        favorite_item_for_you.delete()
        favorite_item.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_favorite_item_for_you_service_404(self):
        favorite_item_for_you = FavoriteItemForYou(
            user_id="356",
            recommendations=["1345", "1276", "1461"],
            score=[1, 4, 6, 7],
        )
        favorite_item_for_you.save()

        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_favorite_item_for_you(
                user_id="358", candidate_count=3, **filter_args
            )
        favorite_item_for_you.delete()

        assert str(excinfo.value) == "FavoriteItem matching query does not exist."

    def test_get_michaels_popular_item_service(self):
        popular_item = PopularItem(
            group_id=0, recommendations=["1", "2", "3", "4"], score=[4, 6, 7, 1]
        )
        popular_item.save()
        expect = ["1", "2", "4"]
        results = get_michaels_popular_item(candidate_count=3, **filter_args)
        popular_item.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_event_service(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        popular_event = PopularEvent(
            group_id=0, recommendations=["1", "2", "3"], score=[1, 3, 5]
        )
        popular_event.save()
        expect = ["1", "2", "3"]
        results = get_michaels_popular_event(candidate_count=3, event_type="ONLINE")
        popular_event.delete()
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "item_id, expect",
        [
            ("456", ["4"]),
            ("455", []),
        ],
    )
    def test_get_michaels_purchased_together_service(self, item_id, expect):
        purchase_bundle = PurchaseBundle(
            item_id="456", recommendations=["4", "5", "6"], score=[9, 6, 7]
        )
        purchase_bundle.save()
        results = get_michaels_purchased_together(
            item_id=item_id, candidate_count=2, **filter_args
        )
        purchase_bundle.delete()
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "item_id, expect",
        [
            ("678", ["4"]),
            ("679", []),
        ],
    )
    def test_get_michaels_viewed_together_service(self, item_id, expect):
        viewed_together = ViewedTogether(
            item_id="678", recommendations=["4", "5", "6"], score=[9, 6, 7]
        )
        viewed_together.save()
        results = get_michaels_viewed_together(
            item_id=item_id, candidate_count=2, **filter_args
        )
        viewed_together.delete()
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "item_id_pt, item_id_vt, expect",
        [
            ("15374", "15374", ["8", "4", "7", "2", "1"]),
            ("15374", "11348", ["1", "2", "4", "8"]),
            ("11348", "15374", ["4", "7", "8"]),
            ("13825", "25672", []),
        ],
    )
    def test_get_michaels_purchased_and_viewed_together_service(
        self, item_id_pt, item_id_vt, expect
    ):
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
        result = get_michaels_purchased_and_viewed_together(
            item_id="15374", view_weight=4.5, candidate_count=6, **filter_args
        )
        purchase_bundle.delete()
        viewed_together.delete()
        assert operator.eq(expect, result)

    def test_put_michaels_user_defined_trending_now_service_case_one(self):
        # Case 1: Adding new category path and recommendations
        expect = {
            "category_path": "root//Frames",
            "recommendations": ["8786", "5435", "9034", "6789"],
        }
        result = put_michaels_user_defined_trending_now(
            category_path="root//Frames", rec_item_ids="8786,5435,9034,6789"
        )
        # Compare new user defined trending now items that are inserted into DB with expected result
        user_def_tn_obj = UserDefTrendingNow.objects(category_path="root//Frames").get()
        user_def_tn_obj.save()
        user_def_tn_obj.delete()
        assert operator.eq(expect, result)
        assert operator.eq(expect["recommendations"], user_def_tn_obj.recommendations)

    def test_put_michaels_user_defined_trending_now_service_case_two(self):
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
        result = put_michaels_user_defined_trending_now(
            category_path="root//Paints", rec_item_ids="100,200,300,500"
        )
        # Compare new user defined trending now items that are updated into DB with expected result
        user_def_tn_obj = UserDefTrendingNow.objects(category_path="root//Paints").get()
        user_def_tn_obj.save()
        user_def_tn_obj.delete()
        disconnect_local_connection(local_conn)
        assert operator.eq(expect, result)
        assert operator.eq(expect["recommendations"], user_def_tn_obj.recommendations)

    def test_put_michaels_user_defined_trending_now_service_case_three(self):
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
        result = put_michaels_user_defined_trending_now(
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
    def test_get_michaels_user_defined_trending_now_service_case_one_two(
        self, category_path, recommendations, expected
    ):
        # case 1: has category path and recommendations and case 2: has category path and no recommendations
        user_def_tn = UserDefTrendingNow(
            category_path=category_path, recommendations=recommendations
        )
        user_def_tn.save()
        results = get_michaels_user_defined_trending_now(
            category_path=category_path,
            candidate_count=2,
            **filter_args,
        )
        user_def_tn.delete()
        assert operator.eq(expected, results)

    def test_get_michaels_user_defined_trending_now_service_case_three(self):
        # Case 3: has no category path
        expect = []
        result = get_michaels_user_defined_trending_now(
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
    def test_get_michaels_trending_now_model_service_case_one_two(
        self, category_path, recommendations, expected
    ):
        # case 1 : recommendations exist and case 2: recommendations doesn't exist
        trending_now = TrendingNowModel(
            category_path=category_path, recommendations=recommendations
        )
        trending_now.save()
        results = get_michaels_trending_now_model(
            category_path=category_path,
            candidate_count=3,
            **filter_args,
        )
        trending_now.delete()
        assert operator.eq(expected, results)

    def test_get_michaels_trending_now_model_service_case_three(self):
        # Case 3: has no category path
        expect = []
        result = get_michaels_trending_now_model(
            category_path="aaa",
            candidate_count=2,
            **filter_args,
        )
        assert operator.eq(expect, result)

    def test_get_michaels_trending_now_service_case_one(self):
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
        results = get_michaels_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        user_tn.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_trending_now_service_case_two(self):
        # Case 2: has user define category path but recommendations empty
        model_tn = TrendingNowModel(
            category_path="abc", recommendations=["1", "2", "3"]
        )
        user_tn = UserDefTrendingNow(category_path="abc", recommendations=[])
        model_tn.save()
        user_tn.save()
        expect = ["1", "2"]
        results = get_michaels_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        user_tn.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_trending_now_service_case_three(self):
        # Case 3: has no user define category path but has model category path
        model_tn = TrendingNowModel(
            category_path="abc", recommendations=["1", "2", "3"]
        )
        model_tn.save()
        expect = ["1", "2"]
        results = get_michaels_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_trending_now_service_case_four(self):
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
        result = get_michaels_trending_now(
            category_path="def",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        user_tn.delete()
        assert operator.eq(expect, result)

    def test_get_michaels_trending_now_service_case_five(self):
        # Case 5: has no user define category path and model recommendation is empty
        model_tn = TrendingNowModel(category_path="abc", recommendations=[])
        model_tn.save()
        expect = []
        results = get_michaels_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )

        model_tn.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_trending_now_all_category_service_case_one(self):
        # Case 1: has both user defined and trending now model
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

        results = get_michaels_trending_now_all_category(
            trending_now="mik_tn_coll",
            user_defined_trending_now="mik_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, results)

    def test_get_michaels_trending_now_all_category_service_case_two(self):
        # Case 2: has user defined but no trending now model
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
        expect = [
            {
                "category_path": "root//Shop Categories",
                "recommendations": ["1", "2"],
            },
            {"category_path": "root//Brushes", "recommendations": ["4"]},
        ]

        results = get_michaels_trending_now_all_category(
            trending_now="mik_tn_coll",
            user_defined_trending_now="mik_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, results)

    def test_get_michaels_trending_now_all_category_service_case_three(self):
        # Case 3: has trending now model but user defined model is empty
        local_conn1, local_col1 = create_local_connection(collection_name="mik_tn_coll")
        local_conn2, local_col2 = create_local_connection(
            collection_name="mik_udf_tn_coll"
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

        results = get_michaels_trending_now_all_category(
            trending_now="mik_tn_coll",
            user_defined_trending_now="mik_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, results)

    def test_get_michaels_trending_now_all_category_service_case_four(self):
        # Case 4: has no user defined model or trending now model
        expect = []
        results = get_michaels_trending_now_all_category(
            trending_now="mik_tn_coll",
            user_defined_trending_now="mik_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        assert operator.eq(expect, results)

    def test_get_michaels_featured_category_service(self):
        featured_category = FeaturedCategory(
            user_id=231,
            recommendations=["root//Accessories//Barrettes", "root//Paint//Acrylic"],
            score=[8, 10],
        )
        popular_category = PopularCategory(
            group_id=0,
            recommendations=["root//Paint//Canvas", "root//Accessories//Whiteboard"],
            score=[7, 11],
        )
        featured_category.save()
        popular_category.save()
        expect = ["root//Paint//Canvas", "root//Accessories//Whiteboard"]
        results = get_michaels_featured_category(user_id=232, candidate_count=2)
        featured_category.delete()
        popular_category.delete()
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "user_id, expect",
        [
            (3331, ["1", "2"]),
            (4333, []),
        ],
    )
    def test_get_michaels_buy_it_again_service(self, user_id, expect):
        buy_it_again = BuyItAgain(
            user_id=3331, recommendations=["1", "2", "3"], score=[3, 5, 8]
        )
        buy_it_again.save()
        results = get_michaels_buy_it_again(
            user_id=user_id, candidate_count=3, **filter_args
        )
        buy_it_again.delete()
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "user_id, expect",
        [
            (3331, ["1", "2"]),
            (4333, []),
        ],
    )
    def test_get_michaels_buy_it_again_mpg_service(self, user_id, expect):
        buy_it_again_mpg = BuyItAgainMPG(
            user_id=3331, recommendations=["1", "2", "3"], score=[9, 5, 8]
        )
        buy_it_again_mpg.save()
        results = get_michaels_buy_it_again_mpg(
            user_id=user_id, candidate_count=3, **filter_args
        )
        buy_it_again_mpg.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_search_keyword_service(self):
        popular_search_keywords = PopularSearchKeyword(
            group_id=0, recommendations=["Popular", "Search", "Terms"], score=[7, 6, 5]
        )
        popular_search_keywords.save()
        expect = ["Popular", "Search", "Terms"]
        results = get_michaels_popular_search_keyword(candidate_count=3)
        popular_search_keywords.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_search_keyword_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_popular_search_keyword(candidate_count=3)
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
    def test_get_michaels_rec_for_you_search_service_case_one_two(
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
        results = get_michaels_rec_for_you_search(user_id=user_id, candidate_count=3)
        rec_for_you_search.delete()
        popular_search_keywords.delete()
        assert operator.eq(expected, results)

    def test_get_michaels_rec_for_you_search_service_case_three(self):
        # If no search recommendations exist
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_rec_for_you_search(user_id=4, candidate_count=3)
        assert (
            str(excinfo.value) == "PopularSearchKeyword matching query does not exist."
        )

    def test_get_michaels_people_also_buy_service(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="777", recommendations=["1", "2", "3"], score=[3, 5, 8]
        )
        people_also_buy.save()
        expect = ["1", "2"]
        results = get_michaels_people_also_buy(
            item_id="777", candidate_count=2, **filter_args
        )
        people_also_buy.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_people_also_buy_service_failed(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="999", recommendations=["14", "15", "16"], score=[1, 2, 9]
        )
        people_also_buy.save()
        expect = []
        results = get_michaels_people_also_buy(
            item_id="99",
            candidate_count=2,
            **filter_args,
        )
        people_also_buy.delete()
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "item_id, recommendations, expected",
        [("777", ["1", "2", "3"], ["1", "2"]), ("999", [], [])],
    )
    def test_get_michaels_people_also_view_service(
        self, item_id, recommendations, expected
    ):
        people_also_view = PeopleAlsoView(
            item_id="777", recommendations=recommendations, score=[3, 5, 8]
        )
        people_also_view.save()
        results = get_michaels_people_also_view(
            item_id=item_id, candidate_count=2, **filter_args
        )
        people_also_view.delete()
        assert operator.eq(expected, results)

    @pytest.mark.parametrize(
        "recommendations, expected",
        [
            (["1", "2", "3"], ["1", "2"]),
            ([], []),
        ],
    )
    def test_get_michaels_seasonal_top_picks_service(self, recommendations, expected):
        # case 1: recommendations exist and case 2: recommendations don't exist
        seasonal_top_picks = SeasonalTopPicks(
            group_id=0, recommendations=recommendations, score=[7, 6, 9]
        )
        seasonal_top_picks.save()
        results = get_michaels_seasonal_top_picks(candidate_count=2, **filter_args)
        seasonal_top_picks.delete()
        assert operator.eq(expected, results)

    def test_get_michaels_project_use_this_service(self):
        project_use_this = ProjectUseThis(
            item_id="77", recommendations=["1", "2", "3"], score=[3, 5, 8]
        )
        project_use_this.save()
        expect = ["1", "2"]
        results = get_michaels_project_use_this(
            item_id="77", candidate_count=2, **project_filter_args
        )
        project_use_this.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_project_use_this_service_failed(self):
        project_use_this = ProjectUseThis(
            item_id="77", recommendations=["4", "2", "6"], score=[3, 5, 8]
        )
        project_use_this.save()
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_project_use_this(
                item_id="9", candidate_count=2, **project_filter_args
            )
        project_use_this.delete()
        assert str(excinfo.value) == "ProjectUseThis matching query does not exist."

    def test_get_michaels_project_inspiration_service(self):
        project_inspiration = ProjectInspiration(
            user_id=202, recommendations=["1", "2", "3"], score=[6, 9, 8]
        )
        project_inspiration.save()
        expect = ["1", "2"]
        results = get_michaels_project_inspiration(
            user_id=202, candidate_count=2, **project_filter_args
        )
        project_inspiration.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_project_inspiration_service_failed(self):
        project_inspiration = ProjectInspiration(
            user_id=303, recommendations=["300", "200", "100"], score=[8, 5, 7]
        )
        popular_project = PopularProject(
            group_id=0, recommendations=["1", "2", "3"], score=[4, 7, 10]
        )
        project_inspiration.save()
        popular_project.save()
        expect = ["1", "2"]
        results = get_michaels_project_inspiration(
            user_id=313, candidate_count=2, **project_filter_args
        )
        project_inspiration.delete()
        popular_project.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_similar_projects_service(self):
        project_similarity = ProjectSimilarity(
            external_id="1003", recommendations=["1", "2", "3"], score=[1, 2, 8]
        )
        project_similarity.save()
        expect = ["1", "2"]
        results = get_michaels_similar_projects(
            candidate_count=2, external_id="1003", **project_filter_args
        )
        project_similarity.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_similar_projects_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_similar_projects(
                candidate_count=3, external_id="1005", **project_filter_args
            )
        assert str(excinfo.value) == "ProjectSimilarity matching query does not exist."

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
    def test_get_michaels_similar_items_for_bundle_service_case_one_to_four(
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
        results = get_michaels_similar_items_for_bundle(
            items_id_list=items_id_list,
            candidate_count=3,
            collection_name="test_collection",
            redis_similar_items_hash_key="mik_similar_items",
            **filter_args,
        )
        redis_client.delete(redis_similar_items_hkey)
        assert operator.eq(expected, results)

    @pytest.mark.parametrize(
        "items_id_list",
        [",", "item123"],
    )
    def test_get_michaels_similar_items_for_bundle_service_case_five_six(
        self, items_id_list
    ):
        # Case 5: Items with invalid items_id_list input
        # Case 6: Items with invalid items_id
        try:
            get_michaels_similar_items_for_bundle(
                items_id_list=items_id_list,
                candidate_count=3,
                collection_name="mik_similar_items",
                redis_similar_items_hash_key="mik_similar_items",
                **filter_args,
            )
        except DoesNotExist:
            assert True
        else:
            assert False

    def test_get_michaels_similar_events_service(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        event_similarity = SimilarEvents(
            event_id="12003", recommendations=["1", "2", "3"], score=[2, 6, 8]
        )
        event_similarity.save()
        expect = ["1", "2", "3"]
        results = get_michaels_similar_events(
            candidate_count=3,
            event_id="12003",
            spanner_table_name="test_events",
            event_type="ONLINE",
        )
        event_similarity.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_similar_events_service_failed(self):
        event_similarity = SimilarEvents(
            event_id="51004", recommendations=["1", "2", "3"], score=[2, 6, 8]
        )
        event_similarity.save()
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_similar_events(
                candidate_count=3,
                event_id="51005",
                spanner_table_name="test_events",
                event_type="ONLINE",
            )
        event_similarity.delete()
        assert str(excinfo.value) == "SimilarEvents matching query does not exist."

    def test_get_michaels_popular_category_service(self):
        popular_category = PopularCategory(
            group_id=0, recommendations=["BB", "CC", "DD"], score=[13, 15, 18]
        )
        popular_category.save()
        expect = ["BB", "CC"]
        results = get_michaels_popular_category(group_id=0, candidate_count=2)
        popular_category.delete()
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("abc", ["1", "2"]),
            ("def", []),
        ],
    )
    def test_get_michaels_popular_item_by_category_service(
        self, category_path, expected
    ):
        # Case 1: With popular item by category data
        # Case 2: Without popular item by category data
        popular_item_by_category = PopularItemByCategory(
            category_path="abc", recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        popular_item_by_category.save()
        result = get_michaels_popular_item_by_category(
            category_path=category_path, candidate_count=2, **filter_args
        )
        popular_item_by_category.delete()
        assert operator.eq(expected, result)

    def test_get_michaels_popular_project_service(self):
        popular_project = PopularProject(
            group_id=0, recommendations=["1", "2", "3"], score=[4, 7, 10]
        )
        popular_project.save()
        expect = ["1", "2"]
        results = get_michaels_popular_project(candidate_count=2, **project_filter_args)
        popular_project.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_project_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_popular_project(
                candidate_count=2,
                **project_filter_args,
            )
        assert str(excinfo.value) == "PopularProject matching query does not exist."

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
    def test_get_michaels_search_people_also_buy_service(
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
            results = get_michaels_search_people_also_buy(
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
    def test_post_michaels_search_rerank_service(
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
            results = post_michaels_search_rerank(json_dict=request_data)
        except Exception as excinfo:
            assert str(excinfo) == expect
        else:
            assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "mock_redis_client",
        [recently_view_redis_data],
        indirect=True,
    )
    def test_michaels_recently_viewed_streaming(self, mock_redis_client):
        rec_api_redis_client = mock_redis_client
        expect = ["1", "2"]
        result = get_michaels_recently_viewed_streaming(
            user_id="123456",
            candidate_count=3,
            date_interval=7,
            **filter_args,
        )
        assert result == expect

    @pytest.mark.parametrize(
        "mock_redis_client",
        [None],
        indirect=True,
    )
    def test_michaels_recently_viewed_streaming_404(self, mock_redis_client):
        rec_api_redis_client = mock_redis_client
        response = get_michaels_recently_viewed_streaming(
            user_id="123456",
            candidate_count=4,
            date_interval=7,
            **filter_args,
        )
        assert response == []

    # @mock.patch("app.main.service.michaels_service.bigquery_client", autospec=True)
    # def test_get_michaels_recently_viewed_service(
    #     self, mock_bigquery_client
    # ):
    #     data = pd.DataFrame([[113, 22], [113, 56]], columns=["user_id", "item_id"])
    #     mock_bigquery_client.query.return_value.result.return_value.to_dataframe.return_value = (
    #         data
    #     )
    #     local_conn, local_col = create_local_connection()
    #     local_col.insert_many(
    #         [
    #             {"item_number": 22, "status": 1},
    #             {"item_number": 56, "status": 1},
    #         ]
    #     )
    #     result = get_michaels_recently_viewed(
    #         user_id="113", candidate_count=4, **filter_args
    #     )
    #     assert result == [22, 56]
    #     disconnect_local_connection(local_conn)
    #
    # @mock.patch("app.main.service.michaels_service.bigquery_client", autospec=True)
    # def test_get_michaels_recently_viewed_service_404(self, mock_bigquery_client):
    #     data = pd.DataFrame([], columns=["user_id", "item_id"])
    #     mock_bigquery_client.query.return_value.result.return_value.to_dataframe.return_value = (
    #         data
    #     )
    #     try:
    #         get_michaels_recently_viewed(
    #             user_id="114",
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
    def test_get_michaels_you_may_also_buy_service(self, user_id, expected):
        # Case 1: With user id
        # Case 2: Without user id
        you_may_also_buy = YouMayAlsoBuy(user_id="777", recommendations=["1", "2", "3"])
        popular_item = PopularItem(
            group_id=0, recommendations=["6", "7", "8"], score=[7, 6, 5]
        )
        you_may_also_buy.save()
        popular_item.save()
        results = get_michaels_you_may_also_buy(
            user_id=user_id, candidate_count=2, **filter_args
        )
        you_may_also_buy.delete()
        popular_item.delete()
        assert operator.eq(expected, results)

    def test_get_michaels_popular_item_by_store_service(self):
        popular_item_by_store = PopularItemByStore(
            store_id=777, recommendations=["8", "7", "6"], score=[8, 7, 6]
        )
        popular_item_by_store.save()
        expect = ["8", "7"]
        results = get_michaels_popular_item_by_store(
            store_id=777,
            candidate_count=2,
            **filter_args,
        )
        popular_item_by_store.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_item_by_store_failed(self):
        popular_item_by_store = PopularItemByStore(
            store_id=777, recommendations=["8", "7", "6"], score=[8, 7, 6]
        )

        popular_item_by_store.save()

        result = get_michaels_popular_item_by_store(
            store_id=77,
            candidate_count=2,
            **filter_args,
        )
        popular_item_by_store.delete()
        assert result == []

    @pytest.mark.parametrize(
        "items_id_list, expected",
        [
            ("1001 1002 1003", ["2", "1"]),
            ("1004", []),
        ],
    )
    def test_get_michaels_purchased_together_bundle_service_case_one_two(
        self, mongo_insert_items_list, items_id_list, expected
    ):
        # Case 1: With valid item_id_list
        # Case 2: Without valid item_list
        result = get_michaels_purchased_together_bundle(
            items_id_list=items_id_list,
            candidate_count=3,
            collection_name="test_collection",
            **filter_args,
        )
        assert operator.eq(expected, result)

    def test_get_michaels_popular_products_in_projects_service(self):
        popular_products_in_projects = PopularProductsInProjects(
            group_id=0, recommendations=["1", "2", "3"], score=[7, 6, 5]
        )
        popular_products_in_projects.save()
        expect = ["1", "2"]
        results = get_michaels_popular_products_in_projects(
            candidate_count=2, **filter_args
        )
        popular_products_in_projects.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_products_in_projects_empty(self):
        popular_products_in_projects = PopularProductsInProjects(
            group_id=0, recommendations=[], score=[]
        )
        popular_products_in_projects.save()
        results = get_michaels_popular_products_in_projects(
            candidate_count=3, **filter_args
        )
        popular_products_in_projects.delete()
        assert operator.eq(results, [])

    def test_get_michaels_yesterday_popular_item_service(self):
        yesterday_popular_item = YesterdayPopularItem(
            group_id=0, recommendations=["2", "4", "6", "8"], score=[4, 6, 7, 1]
        )
        yesterday_popular_item.save()
        expect = ["2", "4", "8"]
        results = get_michaels_yesterday_popular_item(candidate_count=3, **filter_args)
        yesterday_popular_item.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_yesterday_popular_item_service_404(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_yesterday_popular_item(candidate_count=5, **filter_args)
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
    def test_get_michaels_new_projects_service(self, reccomendations, expected):
        new_projects = NewProjects(group_id=0, recommendations=reccomendations)
        new_projects.save()

        results = get_michaels_new_projects(candidate_count=2, **project_filter_args)
        new_projects.delete()
        assert operator.eq(expected, results)

    def test_get_michaels_upcoming_event_service(
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
        results = get_michaels_upcoming_event(candidate_count=3, event_type="ONLINE")
        upcoming_event.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_upcoming_event_service_failed(self):
        try:
            get_michaels_upcoming_event(candidate_count=2, event_type="ONLINE")
        except DoesNotExist:
            assert True

    def test_get_michaels_trending_event_service(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        trending_event = TrendingEvent(
            group_id=0, recommendations=["1", "2", "3"], score=[11, 33, 54]
        )
        trending_event.save()
        expect = ["1", "2", "3"]
        results = get_michaels_trending_event(candidate_count=3, event_type="ONLINE")
        trending_event.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_trending_event_service_404(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_trending_event(candidate_count=2, event_type="ONLINE")
        assert str(excinfo.value) == "TrendingEvent matching query does not exist."

    def test_get_michaels_popular_clearance_category_service(self):
        popular_clearance_category = PopularClearanceCategory(
            group_id=0, recommendations=["BB", "CC", "DD"], score=[18, 15, 13]
        )
        popular_clearance_category.save()
        expect = ["BB", "CC"]
        results = get_michaels_popular_clearance_category(candidate_count=2)
        popular_clearance_category.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_clearance_category_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_popular_clearance_category(candidate_count=2)
        assert (
            str(excinfo.value)
            == "PopularClearanceCategory matching query does not exist."
        )

    def test_get_michaels_popular_sale_category_service(self):
        popular_sale_category = PopularSaleCategory(
            group_id=0, recommendations=["BB", "CC", "DD"], score=[18, 15, 13]
        )
        popular_sale_category.save()
        expect = ["BB", "CC"]
        results = get_michaels_popular_sale_category(candidate_count=2)
        popular_sale_category.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_sale_category_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_popular_sale_category(candidate_count=2)
        assert (
            str(excinfo.value) == "PopularSaleCategory matching query does not exist."
        )

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            ("user1", ["item101", "item103"]),
            ("", ["item101", "item103"]),
        ],
    )
    def test_get_michaels_popular_clearance_item_case_one_two(
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
        result = get_michaels_popular_clearance_item(
            candidate_count=2,
            user_id=user_id,
            redis_popular_clearance_item_hash_key="mik_streaming_top_clearance",
            **filter_args,
            **self.filter_badges_args,
        )
        redis_client.delete(redis_popular_clearance_item_hash_key)
        popular_clearance_item.delete()
        assert operator.eq(expected, result)

    def test_get_michaels_popular_clearance_item_404(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_popular_clearance_item(
                candidate_count=2,
                user_id="",
                redis_popular_clearance_item_hash_key="mik_streaming_top_clearance",
                **filter_args,
                **self.filter_badges_args,
            )
        assert (
            str(excinfo.value) == "PopularClearanceItem matching query does not exist."
        )

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            ("user1", ["item101", "item103"]),
            ("", ["item101", "item103"]),
        ],
    )
    def test_get_michaels_popular_sale_item_case_one_two(
        self, mongo_filter_item_with_badge, user_id, expected
    ):
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
        result = get_michaels_popular_sale_item(
            candidate_count=2,
            user_id=user_id,
            redis_popular_sale_item_hash_key="mik_streaming_top_sale",
            **filter_args,
            **self.filter_badges_args,
        )
        redis_client.delete(redis_popular_sale_item_hash_key)
        popular_sale_item.delete()
        assert operator.eq(expected, result)

    def test_get_michaels_popular_sale_item_404(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_popular_sale_item(
                candidate_count=2,
                user_id="",
                redis_popular_sale_item_hash_key="mik_streaming_top_sale",
                **filter_args,
                **self.filter_badges_args,
            )
        assert str(excinfo.value) == "PopularSaleItem matching query does not exist."

    def test_get_michaels_popular_visited_events_service(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
    ):
        popular_visited_events = PopularVisitedEvents(
            group_id=0, recommendations=["1001", "1002", "1003"], score=[18, 15, 13]
        )
        popular_visited_events.save()
        expect = ["1", "2", "3"]
        results = get_michaels_popular_visited_events(
            candidate_count=2, event_type="ONLINE"
        )
        popular_visited_events.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_visited_events_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_popular_visited_events(candidate_count=2, event_type="ONLINE")
        assert (
            str(excinfo.value) == "PopularVisitedEvents matching query does not exist."
        )

    # def test_get_michaels_streaming_trending_now_list_service(self):
    #     redis_streaming_trending_now_list_key = michaels_args[
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
    #     results = get_michaels_streaming_trending_now_list(
    #         candidate_count=2,
    #         redis_streaming_trending_now_list_key="mik_streaming_trending_now_list",
    #         **filter_args,
    #     )
    #     redis_client.delete(redis_streaming_trending_now_list_key)
    #     disconnect_local_connection(local_conn)
    #     disconnection(connection)
    #     assert operator.eq(expect, results)
    #
    # def test_get_michaels_streaming_trending_now_list_service_404(self):
    #
    #     try:
    #         get_michaels_streaming_trending_now_list(
    #             candidate_count=2,
    #             redis_streaming_trending_now_list_key="mik_streaming_trending_now_list",
    #             **filter_args,
    #         )
    #     except NotFound:
    #         assert True

    def test_get_michaels_popular_first_layer_category_service(self):
        popular_first_layer_category = PopularFirstLayerCategory(
            group_id=0, recommendations=["A", "B", "C"], score=[18, 15, 13]
        )
        popular_first_layer_category.save()
        expect = ["A", "B"]
        results = get_michaels_popular_first_layer_category(candidate_count=2)
        popular_first_layer_category.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_first_layer_category_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_popular_first_layer_category(candidate_count=2)
        assert (
            str(excinfo.value)
            == "PopularFirstLayerCategory matching query does not exist."
        )

    def test_get_michaels_popular_visited_projects_service(self):
        popular_visited_projects = PopularVisitedProjects(
            group_id=0, recommendations=["1", "2", "3"], score=[18, 15, 13]
        )
        popular_visited_projects.save()
        expect = ["1", "2"]
        results = get_michaels_popular_visited_projects(candidate_count=2)
        popular_visited_projects.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_visited_projects_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_popular_visited_projects(candidate_count=2)
        assert (
            str(excinfo.value)
            == "PopularVisitedProjects matching query does not exist."
        )

    def test_get_michaels_popular_visited_items_service(self):
        popular_visited_items = PopularVisitedItems(
            group_id=0, recommendations=["1", "2", "3"], score=[18, 15, 13]
        )
        popular_visited_items.save()
        expect = ["1", "2"]
        results = get_michaels_popular_visited_items(candidate_count=2)
        popular_visited_items.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_visited_items_service_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_popular_visited_items(candidate_count=2)
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
        ["mik_purchased_together"],
        indirect=True,
    )
    def test_get_michaels_shopping_cart_bundle_service(
        self, mongo_filter_scored_item_with_collection_name, items_id_list, expect
    ):
        # Case 1: get recommendations from purchased_together
        # Case 2: get recommendations from similar_items
        # Case 3: get recommendations from purchased_together and similar_items, remove duplicated recommendations
        # Case 4: get [] for data not found
        redis_similar_items_hkey = michaels_args["similar_items_args"][
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
        results = get_michaels_shopping_cart_bundle(
            items_id_list=items_id_list,
            candidate_count=5,
            purchased_together_collection_name="mik_purchased_together",
            similar_items_collection_name="mik_similar_items",
            redis_similar_items_hash_key="mik_similar_items",
            **filter_args,
        )
        redis_client.delete(redis_similar_items_hkey)
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "mongo_filter_scored_item_with_collection_name",
        ["mik_similar_items"],
        indirect=True,
    )
    def test_get_michaels_shopping_cart_bundle_service_case_five(
        self, mongo_filter_scored_item_with_collection_name
    ):
        # Case 5: get recommendations from collection similar_items
        expect = ["2", "1"]
        results = get_michaels_shopping_cart_bundle(
            items_id_list="103 104",
            candidate_count=5,
            purchased_together_collection_name="mik_purchased_together",
            similar_items_collection_name="mik_similar_items",
            redis_similar_items_hash_key="mik_similar_items",
            **filter_args,
        )
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "item_id, expected",
        [
            ("456", ["1", "4"]),
            ("455", []),
        ],
    )
    def test_get_michaels_similar_items_in_same_store_service(self, item_id, expected):
        # Case 1: item exists in mongodb
        # Case 2: item doesn't exists
        similar_items_in_same_store = SimilarItemsInSameStore(
            item_id=item_id, recommendations=["1", "4", "7"], score=[6, 1, 9]
        )
        similar_items_in_same_store.save()
        results = get_michaels_similar_items_in_same_store(
            item_id="456", candidate_count=2, **filter_args
        )
        similar_items_in_same_store.delete()
        assert operator.eq(expected, results)

    @pytest.mark.parametrize(
        "recommendations, scores, expect",
        [
            (["1", "2", "3"], [7, 6, 5], ["1", "2"]),
            ([], [], []),
        ],
    )
    def test_get_michaels_popular_products_in_events_service(
        self, recommendations, scores, expect
    ):
        popular_products_in_events = PopularProductsInEvents(
            group_id=0, recommendations=recommendations, score=scores
        )

        popular_products_in_events.save()
        results = get_michaels_popular_products_in_events(
            candidate_count=2, **filter_args
        )
        popular_products_in_events.delete()
        assert operator.eq(expect, results)

    def test_get_michaels_popular_products_in_events_404(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_michaels_popular_products_in_events(candidate_count=5, **filter_args)
        assert (
            str(excinfo.value)
            == "PopularProductsInEvents matching query does not exist."
        )

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
    def test_get_michaels_related_categories_by_category_service(
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

        result = get_michaels_related_categories_by_category(
            category_path=category_path, candidate_count=2, collection_name="test_sch"
        )
        related_categories_by_category.delete()
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
        ["mik_popular_master_items"],
        indirect=True,
    )
    def test_get_michaels_similar_items_by_popularity_service(
        self, input_item_id, expected, mongo_similar_items_by_popularity
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
        results = get_michaels_similar_items_by_popularity(
            item_id=input_item_id,
            collection_name=collection_name,
            candidate_count=5,
            redis_similar_items_hash_key="mik_similar_items",
            **filter_args,
        )
        redis_client.delete(redis_similar_items_hkey)
        assert operator.eq(expected, results)

    @pytest.mark.parametrize(
        "query_keyword, expected",
        [("query_input", ["1", "2", "3"]), ("invalid_query_input", [])],
    )
    def test_get_michaels_related_queries_by_query_service(
        self, query_keyword, expected
    ):
        related_queries = RelatedQueriesByQuery(
            query="query_input", recommendations=["1", "2", "3"], score=[7, 6, 5]
        )

        related_queries.save()
        results = get_michaels_related_queries_by_query(
            candidate_count=3,
            query_keyword=query_keyword,
        )
        related_queries.delete()
        assert operator.eq(expected, results)

    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("category_input", ["query1", "query2"]),
            ("invalid_category_input", []),
        ],
    )
    def test_get_michaels_related_queries_by_category_service(
        self, category_path, expected
    ):
        related_queries_by_category = RelatedQueriesByCategory(
            category_path="category_input",
            recommendations=["query1", "query2", "query3"],
        )
        related_queries_by_category.save()
        result = get_michaels_related_queries_by_category(
            category_path=category_path,
            candidate_count=2,
        )
        related_queries_by_category.delete()
        assert operator.eq(expected, result)

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
    def test_get_michaels_related_categories_by_query_service(
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
        result = get_michaels_related_categories_by_query(
            query_keyword=query_keyword, candidate_count=2, collection_name="test_sch"
        )
        related_categories_by_query.delete()
        assert operator.eq(expected, result)

    @pytest.mark.parametrize(
        "mongo_filter_inactive_item_with_collection_name, mongo_filter_inactive_category",
        [(test_pfe, test_pfe)],
        indirect=True,
    )
    class TestGetMichaelsPicksFromExpectsService:
        def test_get_michaels_picks_from_experts_case_one(
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
            result = get_michaels_picks_from_experts(
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

        def test_get_michaels_picks_from_experts_case_two(
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
            result = get_michaels_picks_from_experts(
                user_id=0,
                category_count=2,
                category_buffer=2,
                candidate_count=2,
                collection_name=test_pfe,
                **filter_args,
            )
            popular_first_layer_category.delete()
            assert operator.eq(expect, result)

        def test_get_michaels_picks_from_experts_case_three(
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
            result = get_michaels_picks_from_experts(
                user_id=11,
                category_count=2,
                category_buffer=2,
                candidate_count=2,
                collection_name=test_pfe,
                **filter_args,
            )
            featured_first_layer_category.delete()
            assert operator.eq(expect, result)

        def test_get_michaels_picks_from_experts_case_four(
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
                get_michaels_picks_from_experts(
                    user_id=11,
                    category_count=2,
                    category_buffer=2,
                    candidate_count=2,
                    collection_name=test_pfe,
                    **filter_args,
                )
            featured_first_layer_category.delete()
            assert str(excinfo.value.detail) == "Not enough recommendations"

        def test_get_michaels_picks_from_experts_case_five(
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
                get_michaels_picks_from_experts(
                    user_id=11,
                    category_count=2,
                    category_buffer=2,
                    candidate_count=2,
                    collection_name=test_pfe,
                    **filter_args,
                )
            featured_first_layer_category.delete()
            assert str(excinfo.value.detail) == "Not enough recommendations"

        def test_get_michaels_picks_from_experts_case_six(
            self,
            mongo_filter_inactive_item_with_collection_name,
            mongo_filter_inactive_category,
        ):
            # None of featured_first_layer or popular_first_layer exist
            with pytest.raises(NotEnoughRecommendations) as excinfo:
                get_michaels_picks_from_experts(
                    user_id=999,
                    category_count=2,
                    candidate_count=2,
                    category_buffer=2,
                    collection_name=test_pfe,
                    **filter_args,
                )
            assert str(excinfo.value.detail) == "Not enough recommendations"

        def test_get_michaels_picks_from_experts_case_seven(
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
                get_michaels_picks_from_experts(
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

        def test_get_michaels_picks_from_experts_case_eight(
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
                get_michaels_picks_from_experts(
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
