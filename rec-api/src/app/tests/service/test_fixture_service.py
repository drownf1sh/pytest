import json
import operator

import pytest

from app.main import glb_db_conn, redis_client
from app.main.model.michaels import (
    UserRecommend,
    EventForYou,
    RelatedCategoriesByCategory,
)
from app.main.service.michaels_service import (
    get_michaels_recommended_for_you,
    get_michaels_similar_items,
    get_michaels_event_for_you,
    get_michaels_related_categories_by_category,
)
from app.main.util.controller_args import michaels_args
from app.main.util.global_vars import ad_items_status_redis_hkey


class TestMichaelsFixtureService:
    filter_args = {
        "table_name": "test_col",
        "item_col_name": "item_number",
        "check_col_name": "status",
        "check_val": 1,
        "db_connection": glb_db_conn,
    }

    # This example test uses mongo connection object and filter inactive item values
    def test_recommended_for_you_case_one(self):
        # Case 1: recommend_for_you object exists
        user_recommend = UserRecommend(
            user_id=321, recommendations=["3", "5", "2", "1"], score=[1, 5, 3, 6]
        )
        user_recommend.save()
        expect = ["2", "1"]
        results = get_michaels_recommended_for_you(
            user_id=321, candidate_count=3, **self.filter_args
        )
        user_recommend.delete()
        assert operator.eq(expect, results)

    # This example test uses redis connection
    def test_similar_items_case_one(self):
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
        result = get_michaels_similar_items(
            item_id="item1",
            candidate_count=2,
            redis_similar_items_hash_key="mik_similar_items",
            similar_items_api=True,
            **self.filter_args,
        )
        redis_client.delete(
            ad_items_status_redis_hkey,
            redis_similar_items_hkey,
        )
        assert operator.eq(expect, result)

    # This example test uses mock archived events and schedule events
    def test_event_for_you_service(
        self,
        mock_filter_archived_events_in_mongo,
        mock_filter_no_schedule_events_in_mongo,
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

    # This example test uses parametrize
    @pytest.mark.parametrize(
        "category_path, expected",
        [
            ("category_input", ["category1", "category2"]),
            ("invalid_category_input", []),
        ],
    )
    def test_related_categories_by_category(self, category_path, expected):
        related_categories_by_category = RelatedCategoriesByCategory(
            category_path="category_input",
            recommendations=["category1", "category2", "category3"],
        )
        related_categories_by_category.save()
        result = get_michaels_related_categories_by_category(
            category_path=category_path,
            candidate_count=2,
        )
        related_categories_by_category.delete()
        assert operator.eq(expected, result)
