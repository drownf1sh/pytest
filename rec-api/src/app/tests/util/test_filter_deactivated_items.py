import operator

import pytest
import pandas as pd
import datetime

from app.main.util.filter_deactivated_items import filter_deactivated_items
from app.main.util.filter_deactivated_items import filter_deactivated_items_df
from app.main.util.filter_deactivated_items import (
    filter_deactivated_items_in_time_range,
)
from pymongo import MongoClient
from app.main import glb_db_conn


class TestFilterDeactivatedItems:
    recommendation_list = ["1", "2", "10000", "4", "10001", "5", "10002"]
    recommendation_df = pd.DataFrame(
        [
            ["item1", ["1", "2", "10000"]],
            ["item2", ["10001", "5", "10002"]],
        ],
        columns=["item_id", "recommendations"],
    )

    def test_filter_deactivated_items(self):
        client = MongoClient("mongodb://localhost:27017/")
        test_db = client["test"]
        collection = test_db["test_col"]
        collection.insert_many(
            [
                {"item_number": "10000", "item_status": "Active"},
                {"item_number": "10002", "item_status": "A"},
                {"item_number": "10001", "item_status": "Deactivate"},
            ]
        )
        expect = ["10000", "10002"]
        result = filter_deactivated_items(
            recommendation_list=self.recommendation_list,
            db_connection=glb_db_conn,
            table_name="test_col",
            item_col_name="item_number",
            check_col_name="item_status",
            check_val={"$regex": "^A"},
            return_number=2,
        )
        client.drop_database("test")
        assert operator.eq(expect, result)

    def test_filter_deactivated_items_empty(self):
        result = filter_deactivated_items(
            recommendation_list=self.recommendation_list,
            db_connection=glb_db_conn,
            table_name="test_col",
            item_col_name="item_number",
            check_col_name="item_status",
            check_val={"$regex": "^A"},
            return_number=2,
        )
        assert operator.eq([], result)

    def test_filter_deactivated_items_df(self):
        client = MongoClient("mongodb://localhost:27017/")
        test_db = client["test"]
        collection = test_db["test_col"]
        collection.insert_many(
            [
                {"item_number": "10000", "item_status": "Active"},
                {"item_number": "10002", "item_status": "A"},
                {"item_number": "10001", "item_status": "Deactivate"},
            ]
        )
        expect = pd.DataFrame(
            [
                ["item1", ["10000"]],
                ["item2", ["10002"]],
            ],
            columns=["item_id", "recommendations"],
        )
        result = filter_deactivated_items_df(
            recommendation_df=self.recommendation_df,
            rec_col="recommendations",
            return_number=5,
            db_connection=glb_db_conn,
            table_name="test_col",
            item_col_name="item_number",
            check_col_name="item_status",
            check_val={"$regex": "^A"},
        )
        client.drop_database("test")
        assert expect.equals(result)

    def test_filter_deactivated_items_in_time_range(self):
        client = MongoClient("mongodb://localhost:27017/")
        test_db = client["test"]
        collection = test_db["test_col"]
        current_time = datetime.datetime.utcnow()
        collection.insert_many(
            [
                {
                    "item_number": "10000",
                    "item_status": "A",
                    "badges": {
                        "badges_check_name": True,
                        "start_time": (current_time - datetime.timedelta(days=3)),
                        "end_time": (current_time + datetime.timedelta(days=3)),
                    },
                },
                {
                    "item_number": "10001",
                    "item_status": "A",
                    "badges": {
                        "badges_check_name": False,
                        "start_time": (current_time - datetime.timedelta(days=3)),
                        "end_time": (current_time + datetime.timedelta(days=1)),
                    },
                },
                {
                    "item_number": "10002",
                    "item_status": "Deactivate",
                    "badges": {
                        "badges_check_name": True,
                        "start_time": (current_time - datetime.timedelta(days=3)),
                        "end_time": (current_time + datetime.timedelta(days=3)),
                    },
                },
                {
                    "item_number": "4",
                    "item_status": "A",
                    "badges": {
                        "badges_check_name": True,
                        "start_time": (current_time - datetime.timedelta(days=5)),
                        "end_time": (current_time - datetime.timedelta(days=3)),
                    },
                },
            ]
        )
        expect = ["10000"]
        result = filter_deactivated_items_in_time_range(
            recommendation_list=self.recommendation_list,
            db_connection=glb_db_conn,
            table_name="test_col",
            item_col_name="item_number",
            check_col_name="item_status",
            check_val={"$regex": "^A"},
            badges_name="badges",
            badges_check_name="badges_check_name",
            badges_check_val=True,
            current_time=current_time,
            badges_start_date_name="start_time",
            badges_expiration_date_name="end_time",
            return_number=1,
        )
        client.drop_database("test")
        assert operator.eq(expect, result)


if __name__ == "__main__":
    pytest.main()
