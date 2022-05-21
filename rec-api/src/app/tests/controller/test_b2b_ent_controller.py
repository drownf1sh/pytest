import json
import operator

import pytest

from app.main import create_app
from app.main.model.b2b_ent import (
    PurchaseBundle,
    UserRecommend,
    FeaturedCategory,
    BuyItAgain,
    PeopleAlsoBuy,
    SeasonalTopPicks,
    BuyItAgainMPG,
    RecForYouSearch,
    TrendingNowModel,
    UserDefTrendingNow,
    PopularSearchKeyword,
    YouMayAlsoBuy,
)
from app.main.model.b2b_ent import ProjectUseThis, ProjectInspiration, PopularItem
from app.main.util.test_connection import (
    disconnect_local_connection,
    create_local_connection,
)

client = create_app(config_name="test").test_client()

filter_url_string = pytest.filter_url_string
project_filter_url_string = pytest.project_filter_url_string
recently_view_redis_data = pytest.recently_view_redis_data
test_pfe = pytest.test_pfe
test_pab = pytest.test_pab
search_rerank_data = pytest.search_rerank_data


class TestB2BEntController:
    # 200 cases
    @pytest.mark.parametrize(
        "redis_similar_items",
        ["b2b_similar_items"],
        indirect=True,
    )
    def test_similar_items(self, redis_similar_items):
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/b2b_ent/similar_items?item_id=item1&candidate_count=2"
            f"&{filter_url_string}"
        )
        assert operator.eq(expect, json.loads(response.data))

    def test_purchased_together(self):
        purchase_bundle = PurchaseBundle(
            item_id="101",
            recommendations=["1", "2", "3"],
            score=[8, 9, 7],
        )
        purchase_bundle.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/b2b_ent/purchased_together?item_id=101&candidate_count=2"
            f"&{filter_url_string}"
        )
        purchase_bundle.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_add_user_defined_trending_now(self):
        expect = {
            "category_path": "root//Planners",
            "recommendations": ["462525", "57256", "562758", "52645"],
        }
        response = client.put(
            f"/api/rec/b2b_ent/add_user_defined_trending_now?category_path=root%2F%2FPlanners&rec_item_ids=462525%2C57256"
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
            f"/api/rec/b2b_ent/user_defined_trending_now?category_path={category_path}"
            f"&candidate_count=3&{filter_url_string}"
        )
        user_def_tn.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_user_defined_trending_now_404(self):
        response = client.get(
            f"/api/rec/b2b_ent/user_defined_trending_now?category_path=root%2F%2FCustom%20Frames"
            f"&candidate_count=2&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_user_defined_trending_now_bad_request(self):
        response = client.get(
            "/api/rec/b2b_ent/user_defined_trending_now?candidate_count=1"
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
            f"/api/rec/b2b_ent/trending_now_model?category_path={category_path}"
            f"&candidate_count=3&{filter_url_string}"
        )
        trending_now.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_trending_now_model_404(self):
        response = client.get(
            f"/api/rec/b2b_ent/trending_now_model?category_path=root%2F%2FShopping%20Categories"
            f"&candidate_count=2&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_trending_now_model_bad_request(self):
        response = client.get("/api/rec/b2b_ent/trending_now_model?candidate_count=1")
        assert response.status_code == 400

    def test_trending_now(self):
        mod_trending_now = TrendingNowModel(
            category_path="root//Custom Frames",
            recommendations=["4", "5"],
        )
        user_def_tn = UserDefTrendingNow(
            category_path="root//Custom Frames",
            recommendations=["1", "2", "3"],
        )
        mod_trending_now.save()
        user_def_tn.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/b2b_ent/trending_now?category_path=root%2F%2FCustom%20Frames"
            f"&candidate_count=2&{filter_url_string}"
        )
        mod_trending_now.delete()
        user_def_tn.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_trending_now_all_category(self):
        local_conn1, local_col1 = create_local_connection(
            collection_name="b2b_ent_udf_tn_coll"
        )
        local_conn2, local_col2 = create_local_connection(
            collection_name="b2b_ent_tn_coll"
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
        response = client.get(
            f"/api/rec/b2b_ent/trending_now_all_category?user_defined_trending_now=b2b_ent_udf_tn_coll"
            f"&trending_now=b2b_ent_tn_coll&candidate_count=2&{filter_url_string}"
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert operator.eq(expect, json.loads(response.data))

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
            f"/api/rec/b2b_ent/recommended_for_you?user_id={user_id}&{filter_url_string}"
        )
        user_recommend.delete()
        popular_item.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_recommended_for_you_bad_request(self):
        response = client.get("/api/rec/b2b_ent/recommended_for_you?candidate_count=1")
        assert response.status_code == 400

    def test_featured_category(self):
        featured_category = FeaturedCategory(
            user_id=3001,
            recommendations=["root//Accessories//Barrettes", "root//Paint//Acrylic"],
            score=[7, 6, 9],
        )
        featured_category.save()
        expect = ["root//Accessories//Barrettes", "root//Paint//Acrylic"]
        response = client.get("/api/rec/b2b_ent/featured_category?user_id=3001")
        featured_category.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_buy_it_again(self):
        buy_it_again = BuyItAgain(
            user_id=302, recommendations=["3", "2", "1"], score=[2, 4, 6, 9]
        )
        buy_it_again.save()
        expect = ["2", "1"]
        response = client.get(
            f"/api/rec/b2b_ent/buy_it_again?user_id=302&{filter_url_string}"
        )
        buy_it_again.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_buy_it_again_mpg(self):
        buy_it_again_mpg = BuyItAgainMPG(
            user_id=122,
            recommendations=["1", "2", "3", "4"],
            score=[4, 5, 6, 9],
        )
        buy_it_again_mpg.save()
        expect = ["1", "2", "4"]
        response = client.get(
            f"/api/rec/b2b_ent/buy_it_again_mpg?user_id=122&{filter_url_string}"
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
            f"/api/rec/b2b_ent/popular_search_keyword?candidate_count=3"
        )
        popular_search_keyword.delete()
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
        response = client.get(f"/api/rec/b2b_ent/rec_for_you_search?user_id={user_id}")
        rec_for_you_search.delete()
        popular_search_keywords.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_rec_for_you_search_bad_request(self):
        response = client.get("/api/rec/b2b_ent/rec_for_you_search?candidate_count=n")
        assert response.status_code == 400

    def test_people_also_buy(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="033", recommendations=["1", "2", "3"], score=[5, 6, 7]
        )
        people_also_buy.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/b2b_ent/people_also_buy?item_id=033&candidate_count=2&{filter_url_string}"
        )
        people_also_buy.delete()
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
            f"/api/rec/b2b_ent/seasonal_top_picks?candidate_count=2&{filter_url_string}"
        )
        seasonal_top_picks.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_seasonal_top_picks_bad_request(self):
        response = client.get("/api/rec/b2b_ent/seasonal_top_picks?candidate_count")
        assert response.status_code == 400

    def test_project_use_this(self):
        project_use_this = ProjectUseThis(
            item_id="101", recommendations=["1", "2", "3"], score=[6, 2, 4]
        )
        project_use_this.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/b2b_ent/project_use_this?item_id=101"
            f"&candidate_count=2&{project_filter_url_string}"
        )
        project_use_this.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_item(self):
        popular_item = PopularItem(
            group_id=0, recommendations=["1", "2", "3"], score=[2, 6, 9]
        )
        popular_item.save()
        expect = ["1", "2"]
        response = client.get(
            f"/api/rec/b2b_ent/popular_item?group_id=0&candidate_count=2&{filter_url_string}"
        )
        popular_item.delete()
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
            f"/api/rec/b2b_ent/search_people_also_buy?items_scores=2%203&items_id_list=101%20102"
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
            f"/api/rec/b2b_ent/search_people_also_buy?items_id_list=101%20102"
            f"&candidate_count=3&collection_name=test_pab&{filter_url_string}"
        )
        assert operator.eq(expect, json.loads(response.data))

    def test_search_rerank(self, redis_search_rerank):
        # The item vector in the redis is of size(1, 300) but here we are using size(1, 10) vector to test
        data = search_rerank_data[0]
        mimetype = "application/json"
        headers = {"Content-Type": mimetype, "Accept": mimetype}
        expect = {"1022": 0.4082482904638631, "1011": 0.22360679774997896}
        response = client.post(
            "/api/rec/b2b_ent/search_rerank", data=json.dumps(data), headers=headers
        )
        assert operator.eq(expect, json.loads(response.data))

    # 404 cases
    @pytest.mark.parametrize(
        "redis_similar_items",
        ["b2b_similar_items"],
        indirect=True,
    )
    def test_similar_items_404(self, redis_similar_items):
        response = client.get(
            f"/api/rec/b2b_edu/similar_items?item_id=102&candidate_count=2&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_popular_item_404(self):
        popular_item = PopularItem(
            group_id=1, recommendations=["10", "11"], score=[7, 9]
        )
        popular_item.save()
        response = client.get(
            f"/api/rec/b2b_ent/popular_item/group_id=12&{filter_url_string}"
        )
        popular_item.delete()
        assert response.status_code == 404

    def test_purchased_together_404(self):
        purchase_bundle = PurchaseBundle(
            item_id="203", recommendations=["10378", "10131"], score=[4, 9]
        )
        purchase_bundle.save()
        response = client.get(
            f"/api/rec/b2b_ent/purchased_together?item_id=103&candidate_count=2&{filter_url_string}"
        )
        purchase_bundle.delete()
        assert json.loads(response.data) == []

    def test_add_user_defined_trending_now_404(self):
        # Case where list of recommendations is empty
        expect = {"category_path": "root//Planners", "recommendations": []}
        response = client.put(
            f"/api/rec/b2b_ent/add_user_defined_trending_now?category_path=root%2F%2FPlanners"
        )
        user_def_tn_obj = UserDefTrendingNow.objects(
            category_path="root//Planners"
        ).get()
        user_def_tn_obj.save()
        user_def_tn_obj.delete()
        assert operator.eq(expect, json.loads(response.data))
        assert operator.eq(expect["recommendations"], user_def_tn_obj.recommendations)

    def test_trending_now_404(self):
        mod_trending_now = TrendingNowModel(
            category_path="root//Shop Categories",
            recommendations=["3", "4"],
        )
        user_def_tn = UserDefTrendingNow(
            category_path="root//Shop Categories",
            recommendations=["1", "2"],
        )
        mod_trending_now.save()
        user_def_tn.save()
        response = client.get(
            f"/api/rec/b2b_ent/trending_now?category_path=root%2F%2FShopping%20Categories&candidate_count=2&{filter_url_string}"
        )
        mod_trending_now.delete()
        user_def_tn.delete()
        assert json.loads(response.data) == []

    def test_trending_now_all_category_404(self):
        local_conn1, local_col1 = create_local_connection(
            collection_name="b2b_ent_udf_tn_coll"
        )
        local_conn2, local_col2 = create_local_connection(
            collection_name="b2b_ent_tn_coll"
        )
        response = client.get(
            f"/api/rec/b2b_ent/trending_now_all_category?user_defined_trending_now=b2b_ent_udf_tn_coll"
            f"&trending_now=b2b_ent_tn_coll&{filter_url_string}"
        )
        disconnect_local_connection(local_conn1)
        disconnect_local_connection(local_conn2)
        assert json.loads(response.data) == []

    def test_featured_category_404(self):
        featured_category = FeaturedCategory(
            user_id=3002,
            recommendations=["root//Accessories//Barrettes", "root//Paint//Acrylic"],
            score=[3, 9],
        )
        featured_category.save()
        response = client.get("/api/rec/b2b_ent/featured_category?user_id=3003")
        featured_category.delete()
        assert response.status_code == 404

    def test_buy_it_again_404(self):
        buy_it_again = BuyItAgain(
            user_id=12, recommendations=["1", "2", "3"], score=[9, 3, 8]
        )
        buy_it_again.save()
        expect = []
        response = client.get(
            f"/api/rec/b2b_ent/buy_it_again?user_id=2011&{filter_url_string}"
        )
        buy_it_again.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_buy_it_again_mpg_404(self):
        buy_it_again_mpg = BuyItAgainMPG(
            user_id=32, recommendations=["3", "1", "7"], score=[8, 6, 9]
        )
        buy_it_again_mpg.save()
        expect = []
        response = client.get(
            f"/api/rec/b2b_ent/buy_it_again_mpg?user_id=587&{filter_url_string}"
        )
        buy_it_again_mpg.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_popular_search_keyword_404(self):
        response = client.get(
            f"/api/rec/b2b_ent/popular_search_keyword?candidate_count=3"
        )
        assert response.status_code == 404

    def test_people_also_buy_404(self):
        people_also_buy = PeopleAlsoBuy(
            item_id="175", recommendations=["108", "131"], score=[8, 1]
        )
        people_also_buy.save()
        response = client.get(
            f"/api/rec/b2b_ent/people_also_buy?item_id=13&candidate_count=2&{filter_url_string}"
        )
        people_also_buy.delete()
        assert json.loads(response.data) == []

    def test_project_use_this_404(self):
        project_use_this = ProjectUseThis(
            item_id="102", recommendations=["503", "504"], score=[5, 9]
        )
        project_use_this.save()
        response = client.get(
            "/api/rec/b2b_ent/project_use_this?item_id=101&candidate_count=2"
        )
        project_use_this.delete()
        assert response.status_code == 404

    def test_project_inspiration_404(self):
        project_inspiration = ProjectInspiration(
            user_id=61, recommendations=["10", "20", "30"], score=[8, 6, 9]
        )
        project_inspiration.save()
        response = client.get("/api/rec/b2b_ent/project_inspiration?user_id=62")
        project_inspiration.delete()
        assert response.status_code == 404

    def test_search_people_also_buy_404(self):
        response = client.get(
            f"/api/rec/b2b_ent/search_people_also_buy?items_scores=2%203&items_id_list=666%20999&candidate_count=3"
            f"&collection_name=test_col&{filter_url_string}"
        )
        assert response.status_code == 404

    def test_search_rerank_404(self, redis_search_rerank):
        # The item vector in the redis is of size(1, 300) but here we are using size(1, 10) vector to test
        data = search_rerank_data[3]
        mimetype = "application/json"
        headers = {"Content-Type": mimetype, "Accept": mimetype}
        response = client.post(
            "/api/rec/b2b_ent/search_rerank",
            data=json.dumps(data),
            headers=headers,
        )
        assert response.status_code == 404

    # Bad request cases
    def test_similar_items_bad_request(self):
        response = client.get("/api/rec/b2b_ent/similar_items?candidate_count=3")
        assert response.status_code == 400

    def test_add_user_defined_trending_now_bad_request(self):
        response = client.put("/api/rec/b2b_ent/add_user_defined_trending_now")
        assert response.status_code == 400

    def test_trending_now_bad_request(self):
        response = client.get("/api/rec/b2b_ent/trending_now?candidate_count=1")
        assert response.status_code == 400

    def test_trending_now_all_category_bad_request(self):
        response = client.get(
            "/api/rec/b2b_ent/trending_now_all_category?candidate_count=c"
        )
        assert response.status_code == 400

    def test_purchased_together_bad_request(self):
        response = client.get("/api/rec/b2b_ent/purchased_together")
        assert response.status_code == 400

    def test_featured_category_bad_request(self):
        response = client.get("/api/rec/b2b_ent/featured_category?user_id='user1'")
        assert response.status_code == 400

    def test_buy_it_again_bad_request(self):
        response = client.get("/api/rec/b2b_ent/buy_it_again?candidate_count=3")
        assert response.status_code == 400

    def test_buy_it_again_mpg_bad_request(self):
        response = client.get("/api/rec/b2b_ent/buy_it_again_mpg?candidate_count=6")
        assert response.status_code == 400

    def test_popular_search_keyword_bad_request(self):
        response = client.get(
            f"/api/rec/b2b_ent/popular_search_keyword?candidate_count=h"
        )
        assert response.status_code == 400

    def test_people_also_buy_bad_request(self):
        response = client.get("/api/rec/b2b_ent/people_also_buy?candidate_count=3")
        assert response.status_code == 400

    def test_project_use_this_bad_request(self):
        response = client.get("/api/rec/b2b_ent/project_use_this?candidate_count=6")
        assert response.status_code == 400

    def test_popular_item_bad_request(self):
        response = client.get("/api/rec/b2b_ent/popular_item?candidate_count=None")
        assert response.status_code == 400

    def test_search_people_also_buy_bad_request(self):
        response = client.get(
            "/api/rec/b2b_ent/search_people_also_buy?candidate_count=8"
        )
        assert response.status_code == 400

    def test_search_rerank_bad_request(self):
        response = client.post("/api/rec/b2b_ent/search_rerank")
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
            f"/api/rec/b2b_ent/recently_viewed_streaming?user_id=b2b_ent_streaming_recently_view_123"
            f"&candidate_count=3&{filter_url_string}"
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
            f"/api/rec/b2b_ent/recently_viewed_streaming?user_id=b2b_ent_streaming_recently_view_123"
            f"&candidate_count=3&{filter_url_string}"
        )
        assert json.loads(response.data) == []

    def test_recently_viewed_streaming_bad_request(self):
        response = client.get(
            "/api/rec/b2b_ent/recently_viewed_streaming?candidate_count=3"
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
            f"/api/rec/b2b_ent/you_may_also_buy?user_id={user_id}&candidate_count=3"
            f"&{filter_url_string}"
        )
        you_may_also_buy.delete()
        popular_item.delete()
        assert operator.eq(expected, json.loads(response.data))

    def test_you_may_also_buy_bad_request(self):
        response = client.get("/api/rec/b2b_ent/you_may_also_buy?candidate_count=3")
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
            f"/api/rec/b2b_ent/purchased_together_bundle?items_id_list={items_id_list}"
            f"&candidate_count=3&{filter_url_string}&collection_name={collection_name}"
        )
        assert operator.eq(expected, json.loads(response.data))

    def test_purchased_together_bundle_bad_request(self):
        response = client.get(
            "/api/rec/b2b_ent/purchased_together_bundle?candidate_count=3"
        )
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main()
