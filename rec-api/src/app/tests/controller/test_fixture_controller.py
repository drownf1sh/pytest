import json
import operator
import urllib

import pytest
from app.main import redis_client, create_app
from app.main.model.michaels import (
    UserRecommend,
    PopularEvent,
    RelatedCategoriesByCategory,
)
from app.main.util.controller_args import michaels_args
from app.main.util.global_vars import ad_items_status_redis_hkey

client = create_app(config_name="test").test_client()


class TestMichaelsFixtureController:
    filter_url_string = urllib.parse.urlencode(
        {
            "db_name": "test_db",
            "table_name": "test_col",
            "item_col_name": "item_number",
            "check_col_name": "status",
            "check_val": 1,
        },
        doseq=True,
    )

    def test_recommend_for_you(self):
        user_recommend = UserRecommend(
            user_id=999, recommendations=["3", "2", "1"], score=[1, 2, 5]
        )
        user_recommend.save()
        expect = ["2", "1"]
        response = client.get(
            f"/api/rec/michaels/recommended_for_you?user_id=999&{self.filter_url_string}"
        )
        user_recommend.delete()
        assert operator.eq(expect, json.loads(response.data))

    # This example test uses redis connection
    def test_similar_items(self):
        redis_similar_items_hkey = michaels_args["similar_items_args"][
            "redis_similar_items_hash_key"
        ]["default"]
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
        response = client.get(
            f"/api/rec/michaels/similar_items?item_id=item1&candidate_count=2"
            f"&{self.filter_url_string}"
        )
        redis_client.delete(
            ad_items_status_redis_hkey,
            redis_similar_items_hkey,
        )
        assert operator.eq(expect, json.loads(response.data))

    # This example test uses mock events and schedule events
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
            "/api/rec/michaels/popular_event?group_id=0&candidate_count=3&event_type=ONLINE"
        )
        popular_event.delete()
        assert operator.eq(expect, json.loads(response.data))

    # This example test uses parametrize
    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("category_input", ["category1", "category2"]),
            ("invalid_category_input", []),
        ],
    )
    def test_michaels_related_categories_by_category(self, category_path, expected):
        related_categories_by_category = RelatedCategoriesByCategory(
            category_path="category_input",
            recommendations=["category1", "category2", "category3"],
        )
        related_categories_by_category.save()
        response = client.get(
            f"/api/rec/michaels/related_categories_by_category?category_path={category_path}"
            f"&candidate_count=2"
        )
        related_categories_by_category.delete()
        assert operator.eq(expected, json.loads(response.data))
