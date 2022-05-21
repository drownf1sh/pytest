import operator

import pytest
from mongoengine import DoesNotExist

from app.main.model.b2b_edu import (
    PurchaseBundle,
    UserRecommend,
    FeaturedCategory,
    BuyItAgain,
    PeopleAlsoBuy,
    SeasonalTopPicks,
    BuyItAgainMPG,
    RecForYouSearch,
    UserDefTrendingNow,
    TrendingNowModel,
    PopularSearchKeyword,
    YouMayAlsoBuy,
    ItemSimilarity,
)
from app.main.model.b2b_edu import ProjectUseThis, ProjectInspiration, PopularItem
from app.main.service.b2b_edu_service import (
    get_b2b_edu_purchased_together,
    # get_b2b_edu_recently_viewed,
    get_b2b_edu_buy_it_again_mpg,
    get_b2b_edu_search_people_also_buy,
    post_b2b_edu_search_rerank,
    get_b2b_edu_trending_now_model,
    get_b2b_edu_user_defined_trending_now,
    put_b2b_edu_user_defined_trending_now,
    get_b2b_edu_trending_now_all_category,
    get_b2b_edu_popular_search_keyword,
    get_b2b_edu_you_may_also_buy,
    get_b2b_edu_purchased_together_bundle,
    get_b2b_edu_streaming_trending_now_list,
)
from app.main.service.b2b_edu_service import get_b2b_edu_recommended_for_you
from app.main.service.b2b_edu_service import get_b2b_edu_similar_items
from app.main.service.b2b_edu_service import get_b2b_edu_trending_now
from app.main.service.b2b_edu_service import get_b2b_edu_featured_category
from app.main.service.b2b_edu_service import get_b2b_edu_buy_it_again
from app.main.service.b2b_edu_service import get_b2b_edu_people_also_buy
from app.main.service.b2b_edu_service import get_b2b_edu_seasonal_top_picks
from app.main.service.b2b_edu_service import get_b2b_edu_project_use_this
from app.main.service.b2b_edu_service import get_b2b_edu_project_inspiration
from app.main.service.b2b_edu_service import get_b2b_edu_popular_item
from app.main.service.b2b_edu_service import get_b2b_edu_recently_viewed_streaming
from app.main.service.b2b_edu_service import get_b2b_edu_rec_for_you_search
from app.main.util.test_connection import (
    create_local_connection,
    disconnect_local_connection,
)


# global var defined in conftest.py pytest_configure
filter_args = pytest.filter_args
test_pfe = pytest.test_pfe
project_filter_args = pytest.project_filter_args
recently_view_redis_data = pytest.recently_view_redis_data
test_pab = pytest.test_pab
search_rerank_data = pytest.search_rerank_data


class TestB2BEduService:
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
        ["b2b_similar_items"],
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
        result = get_b2b_edu_similar_items(
            item_id=item,
            candidate_count=2,
            redis_similar_items_hash_key="b2b_similar_items",
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
    def test_get_b2b_edu_recommended_for_you_service_case_one_two(
        self, user_id, expected
    ):
        # Case 2: recommend_for_you object does not exist, popular_item object exists
        user_recommend = UserRecommend(
            user_id=321, recommendations=["3", "5", "2", "1"], score=[1, 5, 3, 6]
        )
        popular_item = PopularItem(group_id=0, recommendations=["7", "8", "9"])
        user_recommend.save()
        popular_item.save()
        results = get_b2b_edu_recommended_for_you(
            user_id=user_id, candidate_count=3, **filter_args
        )
        user_recommend.delete()
        popular_item.delete()
        assert operator.eq(expected, results)

    def test_get_b2b_edu_recommended_for_you_service_case_three(self):
        # Case 3: recommend_for_you object, popular_item object do not exist
        with pytest.raises(DoesNotExist) as excinfo:
            get_b2b_edu_recommended_for_you(
                user_id=543, candidate_count=3, **filter_args
            )
        assert str(excinfo.value) == "PopularItem matching query does not exist."

    def test_get_b2b_edu_popular_item_service(self):
        popular_item = PopularItem(
            group_id=0, recommendations=["1", "2", "3", "4"], score=[4, 6, 7, 1]
        )
        popular_item.save()
        expect = ["1", "2", "4"]
        results = get_b2b_edu_popular_item(candidate_count=3, **filter_args)
        popular_item.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_featured_category_service(self):
        featured_category = FeaturedCategory(
            user_id=231,
            recommendations=["root//Accessories//Barrettes", "root//Paint//Acrylic"],
            score=[9, 8],
        )
        featured_category.save()
        expect = ["root//Accessories//Barrettes", "root//Paint//Acrylic"]
        results = get_b2b_edu_featured_category(user_id=231, candidate_count=3)
        featured_category.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_featured_category_service_failed(self):
        featured_category = FeaturedCategory(
            user_id=321,
            recommendations=["root//Accessories//Barrettes", "root//Paint//Acrylic"],
            score=[9, 8],
        )
        featured_category.save()
        with pytest.raises(DoesNotExist) as excinfo:
            get_b2b_edu_featured_category(user_id=322, candidate_count=3)
        featured_category.delete()
        assert str(excinfo.value) == "FeaturedCategory matching query does not exist."

    @pytest.mark.parametrize(
        "item_id, expect",
        [
            ("456", ["4"]),
            ("455", []),
        ],
    )
    def test_get_b2b_edu_purchased_together_service(self, item_id, expect):
        purchase_bundle = PurchaseBundle(
            item_id="456", recommendations=["4", "5", "6"], score=[9, 6, 7]
        )
        purchase_bundle.save()
        results = get_b2b_edu_purchased_together(
            item_id=item_id, candidate_count=2, **filter_args
        )
        purchase_bundle.delete()
        assert operator.eq(expect, results)

    def test_put_b2b_edu_user_defined_trending_now_service_case_one(self):
        # Case 1: Adding new category path and recommendations
        expect = {
            "category_path": "root//Frames",
            "recommendations": ["8786", "5435", "9034", "6789"],
        }
        result = put_b2b_edu_user_defined_trending_now(
            category_path="root//Frames", rec_item_ids="8786,5435,9034,6789"
        )
        # Compare new user defined trending now items that are inserted into DB with expected result
        user_def_tn_obj = UserDefTrendingNow.objects(category_path="root//Frames").get()
        user_def_tn_obj.save()
        user_def_tn_obj.delete()
        assert operator.eq(expect, result)
        assert operator.eq(expect["recommendations"], user_def_tn_obj.recommendations)

    def test_put_b2b_edu_user_defined_trending_now_service_case_two(self):
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
        result = put_b2b_edu_user_defined_trending_now(
            category_path="root//Paints", rec_item_ids="100,200,300,500"
        )
        # Compare new user defined trending now items that are updated into DB with expected result
        user_def_tn_obj = UserDefTrendingNow.objects(category_path="root//Paints").get()
        user_def_tn_obj.save()
        user_def_tn_obj.delete()
        disconnect_local_connection(local_conn)
        assert operator.eq(expect, result)
        assert operator.eq(expect["recommendations"], user_def_tn_obj.recommendations)

    def test_put_b2b_edu_user_defined_trending_now_service_case_three(self):
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
        result = put_b2b_edu_user_defined_trending_now(
            category_path="root//Canvas", rec_item_ids=""
        )
        user_def_tn_obj = UserDefTrendingNow.objects(category_path="root//Canvas").get()
        user_def_tn_obj.save()
        user_def_tn_obj.delete()
        disconnect_local_connection(local_conn)
        assert operator.eq(expect, result)
        assert operator.eq(expect["recommendations"], user_def_tn_obj.recommendations)

    def test_get_b2b_edu_user_defined_trending_now_service_case_one(self):
        # Case 1: has category path and recommendations
        user_def_tn = UserDefTrendingNow(
            category_path="lkj", recommendations=["1", "2", "3"]
        )
        user_def_tn.save()
        expect = ["1", "2"]
        results = get_b2b_edu_user_defined_trending_now(
            category_path="lkj",
            candidate_count=2,
            **filter_args,
        )
        user_def_tn.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_user_defined_trending_now_service_case_two(self):
        # Case 2: has category path and but recommendations is empty
        user_def_tn = UserDefTrendingNow(category_path="qwe", recommendations=[])
        user_def_tn.save()
        expect = []
        results = get_b2b_edu_user_defined_trending_now(
            category_path="qwe",
            candidate_count=2,
            **filter_args,
        )
        user_def_tn.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_user_defined_trending_now_service_case_three(self):
        # Case 3: has no category path
        user_def_tn = UserDefTrendingNow(
            category_path="ikl", recommendations=["43", "27", "619"]
        )
        user_def_tn.save()
        expect = []
        result = get_b2b_edu_user_defined_trending_now(
            category_path="sdf",
            candidate_count=2,
            **filter_args,
        )
        user_def_tn.delete()
        assert operator.eq(expect, result)

    @pytest.mark.parametrize(
        "category_path, recommendations, expected",
        [
            ("abc", ["5", "8", "9"], ["8", "9"]),
            ("def", [], []),
        ],
    )
    def test_get_b2b_edu_trending_now_model_service_case_one_two(
        self, category_path, recommendations, expected
    ):
        # case 1 : recommendations exist and case 2: recommendations doesn't exist
        trending_now = TrendingNowModel(
            category_path=category_path, recommendations=recommendations
        )
        trending_now.save()
        results = get_b2b_edu_trending_now_model(
            category_path=category_path,
            candidate_count=3,
            **filter_args,
        )
        trending_now.delete()
        assert operator.eq(expected, results)

    def test_get_b2b_edu_trending_now_model_service_case_three(self):
        # Case 3: has no category path
        expect = []
        result = get_b2b_edu_trending_now_model(
            category_path="aaa",
            candidate_count=2,
            **filter_args,
        )
        assert operator.eq(expect, result)

    def test_get_b2b_edu_trending_now_service_case_one(self):
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
        results = get_b2b_edu_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        user_tn.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_trending_now_service_case_two(self):
        # Case 2: has user define category path but recommendations empty
        model_tn = TrendingNowModel(
            category_path="abc", recommendations=["1", "2", "3"]
        )
        user_tn = UserDefTrendingNow(category_path="abc", recommendations=[])
        model_tn.save()
        user_tn.save()
        expect = ["1", "2"]
        results = get_b2b_edu_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        user_tn.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_trending_now_service_case_three(self):
        # Case 3: has no user define category path but has model category path
        model_tn = TrendingNowModel(
            category_path="abc", recommendations=["1", "2", "3"]
        )
        model_tn.save()
        expect = ["1", "2"]
        results = get_b2b_edu_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_trending_now_service_case_four(self):
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
        result = get_b2b_edu_trending_now(
            category_path="def",
            candidate_count=2,
            **filter_args,
        )
        model_tn.delete()
        user_tn.delete()
        assert operator.eq(expect, result)

    def test_get_b2b_edu_trending_now_service_case_five(self):
        # Case 5: has no user define category path and model recommendation is empty
        model_tn = TrendingNowModel(category_path="abc", recommendations=[])
        model_tn.save()
        expect = []
        results = get_b2b_edu_trending_now(
            category_path="abc",
            candidate_count=2,
            **filter_args,
        )

        model_tn.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_trending_now_all_category_service_case_one(self):
        # Case 1: has both user defined and trending now model
        local_conn1, local_col1 = create_local_connection(
            collection_name="b2b_edu_udf_tn_coll"
        )
        local_conn2, local_col2 = create_local_connection(
            collection_name="b2b_edu_tn_coll"
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

        results = get_b2b_edu_trending_now_all_category(
            trending_now="b2b_edu_tn_coll",
            user_defined_trending_now="b2b_edu_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, results)

    def test_get_b2b_edu_trending_now_all_category_service_case_two(self):
        # Case 2: has user defined but no trending now model
        local_conn1, local_col1 = create_local_connection(
            collection_name="b2b_edu_udf_tn_coll"
        )
        local_conn2, local_col2 = create_local_connection(
            collection_name="b2b_edu_tn_coll"
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

        results = get_b2b_edu_trending_now_all_category(
            trending_now="b2b_edu_tn_coll",
            user_defined_trending_now="b2b_edu_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, results)

    def test_get_b2b_edu_trending_now_all_category_service_case_three(self):
        # Case 3: has trending now model but user defined model is empty
        local_conn1, local_col1 = create_local_connection(
            collection_name="b2b_edu_tn_coll"
        )
        local_conn2, local_col2 = create_local_connection(
            collection_name="b2b_edu_udf_tn_coll"
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

        results = get_b2b_edu_trending_now_all_category(
            trending_now="b2b_edu_tn_coll",
            user_defined_trending_now="b2b_edu_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, results)

    def test_get_b2b_edu_trending_now_all_category_service_case_four(self):
        # Case 4: has no user defined model or trending now model
        expect = []
        results = get_b2b_edu_trending_now_all_category(
            trending_now="b2b_edu_tn_coll",
            user_defined_trending_now="b2b_edu_udf_tn_coll",
            candidate_count=2,
            **filter_args,
        )
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "user_id, expect",
        [
            (3331, ["1", "2"]),
            (4333, []),
        ],
    )
    def test_get_b2b_edu_buy_it_again_service(self, user_id, expect):
        buy_it_again = BuyItAgain(
            user_id=3331, recommendations=["1", "2", "3"], score=[3, 5, 8]
        )
        buy_it_again.save()
        results = get_b2b_edu_buy_it_again(
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
    def test_get_b2b_edu_buy_it_again_mpg_service(self, user_id, expect):
        buy_it_again_mpg = BuyItAgainMPG(
            user_id=3331, recommendations=["1", "2", "3"], score=[9, 5, 8]
        )
        buy_it_again_mpg.save()
        results = get_b2b_edu_buy_it_again_mpg(
            user_id=user_id, candidate_count=3, **filter_args
        )
        buy_it_again_mpg.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_popular_search_keyword_service(self):
        popular_search_keywords = PopularSearchKeyword(
            group_id=0, recommendations=["Popular", "Search", "Terms"], score=[7, 6, 5]
        )
        popular_search_keywords.save()
        expect = ["Popular", "Search", "Terms"]
        results = get_b2b_edu_popular_search_keyword(candidate_count=3)
        popular_search_keywords.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_popular_search_keyword_failed(self):
        with pytest.raises(DoesNotExist) as excinfo:
            get_b2b_edu_popular_search_keyword(candidate_count=3)
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
    def test_get_b2b_edu_rec_for_you_search_service_case_one_two(
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
        results = get_b2b_edu_rec_for_you_search(user_id=user_id, candidate_count=3)
        rec_for_you_search.delete()
        popular_search_keywords.delete()
        assert operator.eq(expected, results)

    def test_get_b2b_edu_rec_for_you_search_service_case_three(self):
        # If no search recommendations exist
        with pytest.raises(DoesNotExist) as excinfo:
            get_b2b_edu_rec_for_you_search(user_id=4, candidate_count=3)
        assert (
            str(excinfo.value) == "PopularSearchKeyword matching query does not exist."
        )

    def test_get_b2b_edu_people_also_buy_service(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="777", recommendations=["8", "7", "6"], score=[3, 5, 8]
        )
        people_also_buy.save()
        expect = ["8", "7"]
        results = get_b2b_edu_people_also_buy(
            item_id="777", candidate_count=2, **filter_args
        )
        people_also_buy.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_people_also_buy_service_failed(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="999", recommendations=["14", "15", "16"], score=[1, 7, 8]
        )
        people_also_buy.save()
        expect = []
        results = get_b2b_edu_people_also_buy(
            item_id="99",
            candidate_count=2,
            **filter_args,
        )
        people_also_buy.delete()
        assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "recommendations, expected",
        [
            (["1", "2", "3"], ["1", "2"]),
            ([], []),
        ],
    )
    def test_get_b2b_edu_seasonal_top_picks_service(self, recommendations, expected):
        # case 1: recommendations exist and case 2: recommendations don't exist
        seasonal_top_picks = SeasonalTopPicks(
            group_id=0, recommendations=recommendations, score=[7, 6, 9]
        )
        seasonal_top_picks.save()
        results = get_b2b_edu_seasonal_top_picks(candidate_count=2, **filter_args)
        seasonal_top_picks.delete()
        assert operator.eq(expected, results)

    def test_get_b2b_edu_project_use_this_service(self):
        project_use_this = ProjectUseThis(
            item_id="10001", recommendations=["1", "2", "3"], score=[1, 6, 8]
        )
        project_use_this.save()
        expect = ["1", "2"]
        results = get_b2b_edu_project_use_this(
            item_id="10001", candidate_count=2, **project_filter_args
        )
        project_use_this.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_project_use_this_service_failed(self):
        project_use_this = ProjectUseThis(
            item_id="9", recommendations=["114", "115", "116"], score=[4, 9, 8]
        )
        project_use_this.save()
        with pytest.raises(DoesNotExist) as excinfo:
            get_b2b_edu_project_use_this(
                item_id="10", candidate_count=2, **project_filter_args
            )
        project_use_this.delete()
        assert str(excinfo.value) == "ProjectUseThis matching query does not exist."

    def test_get_b2b_edu_project_inspiration_service(self):
        project_inspiration = ProjectInspiration(
            user_id=202, recommendations=["1", "2", "3"], score=[2, 9, 8]
        )
        project_inspiration.save()
        expect = ["1", "2"]
        results = get_b2b_edu_project_inspiration(user_id=202, candidate_count=2)
        project_inspiration.delete()
        assert operator.eq(expect, results)

    def test_get_b2b_edu_project_inspiration_service_failed(self):
        project_inspiration = ProjectInspiration(
            user_id=303, recommendations=["300", "200", "100"], score=[5, 7, 9]
        )
        project_inspiration.save()
        with pytest.raises(DoesNotExist) as excinfo:
            get_b2b_edu_project_inspiration(user_id=313, candidate_count=2)
        project_inspiration.delete()
        assert str(excinfo.value) == "ProjectInspiration matching query does not exist."

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
    def test_get_b2b_edu_search_people_also_buy_service(
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
            results = get_b2b_edu_search_people_also_buy(
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
    def test_post_b2b_edu_search_rerank_service(
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
            results = post_b2b_edu_search_rerank(json_dict=request_data)
        except Exception as excinfo:
            assert str(excinfo) == expect
        else:
            assert operator.eq(expect, results)

    @pytest.mark.parametrize(
        "mock_redis_client",
        [recently_view_redis_data],
        indirect=True,
    )
    def test_b2b_edu_recently_viewed_streaming(self, mock_redis_client):
        rec_api_redis_client = mock_redis_client
        expect = ["1", "2"]
        result = get_b2b_edu_recently_viewed_streaming(
            user_id="123456",
            candidate_count=4,
            date_interval=7,
            **filter_args,
        )
        assert operator.eq(expect, result)

    @pytest.mark.parametrize(
        "mock_redis_client",
        [None],
        indirect=True,
    )
    def test_b2b_edu_recently_viewed_streaming_404(self, mock_redis_client):
        rec_api_redis_client = mock_redis_client
        response = get_b2b_edu_recently_viewed_streaming(
            user_id="123456",
            candidate_count=4,
            date_interval=7,
            **filter_args,
        )
        assert response == []

    @pytest.mark.parametrize(
        "user_id, expected",
        [
            ("777", ["1", "2"]),
            ("99", ["7", "8"]),
        ],
    )
    def test_get_b2b_edu_you_may_also_buy_service(self, user_id, expected):
        # Case 1: With user id
        # Case 2: Without user id
        you_may_also_buy = YouMayAlsoBuy(user_id="777", recommendations=["1", "2", "3"])
        popular_item = PopularItem(
            group_id=0, recommendations=["6", "7", "8"], score=[7, 6, 5]
        )
        you_may_also_buy.save()
        popular_item.save()
        results = get_b2b_edu_you_may_also_buy(
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
    def test_get_b2b_edu_purchased_together_bundle_service_case_one_two(
        self, mongo_insert_items_list, items_id_list, expected
    ):
        # Case 1: With valid item_id_list
        # Case 2: Without valid item_list
        result = get_b2b_edu_purchased_together_bundle(
            items_id_list=items_id_list,
            candidate_count=3,
            collection_name="test_collection",
            **filter_args,
        )
        assert operator.eq(expected, result)

    # def test_get_b2b_edu_streaming_trending_now_list_service(self):
    #     redis_streaming_trending_now_list_key = b2b_args[
    #         "b2b_edu_streaming_trending_now_list_args"
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
    #     results = get_b2b_edu_streaming_trending_now_list(
    #         candidate_count=2,
    #         redis_streaming_trending_now_list_key="b2b_edu_streaming_trending_now_list",
    #         **filter_args,
    #     )
    #     redis_client.delete(redis_streaming_trending_now_list_key)
    #     disconnect_local_connection(local_conn)
    #     disconnection(connection)
    #     assert operator.eq(expect, results)
    #
    # def test_get_b2b_edu_streaming_trending_now_list_service_404(self):
    #     try:
    #         get_b2b_edu_streaming_trending_now_list(
    #             candidate_count=2,
    #             redis_streaming_trending_now_list_key="b2b_edu_streaming_trending_now_list",
    #             **filter_args,
    #         )
    #     except NotFound:
    #         assert True


if __name__ == "__main__":
    pytest.main()
