import operator
import time
import pytest
from pymongo import MongoClient
from app.main import rec_db_conn
from app.main.util.filter_archived_events import (
    filter_no_schedule_events_in_mongo,
    filter_archived_events_in_mongo,
)


class TestFilterArchivedEvents:
    recommendation_list = ["1000", "2000", "3000", "4000", "5000", "6000", "7000"]

    def test_archived_events_in_mongo(self):
        client = MongoClient("mongodb://localhost:27017/")
        test_db = client["test"]
        collection = test_db["test_col"]
        collection.insert_many(
            [
                {"event_id": 1000, "archived": 0, "event_type": "ONLINE"},
                {"event_id": 2000, "archived": 1, "event_type": "PROJECT"},
                {"event_id": 3000, "archived": 0, "event_type": "PROJECT"},
                {"event_id": 4000, "archived": 0, "event_type": "IN_STORE"},
                {"event_id": 5000, "archived": 1, "event_type": "ONLINE"},
                {"event_id": 6000, "archived": 0, "event_type": "ONLINE"},
                {"event_id": 7000, "archived": 0, "event_type": "ONLINE"},
            ]
        )
        expect = [1000, 6000]
        result = filter_archived_events_in_mongo(
            recommendation_list=self.recommendation_list,
            db_connection=rec_db_conn,
            return_number=2,
            event_type_col="ONLINE",
            event_id_str="event_id",
            archived_str="archived",
            event_type_str="event_type",
            archived_event_table_name="test_col",
        )
        client.drop_database("test")
        assert operator.eq(expect, result)

    def test_no_schedule_events_in_mongo(self):
        client = MongoClient("mongodb://localhost:27017/")
        test_db = client["test"]
        collection = test_db["test_col"]
        current_time = time.time_ns() // 1_000_000
        millis_in_an_hour = 3600000
        millis_in_10_minutes = 600000
        millis_in_5_minutes = 300000
        millis_in_7_minutes = 420000
        collection.insert_many(
            [
                {"event_id": 1000, "event_date": (current_time - millis_in_5_minutes)},
                {"event_id": 2000, "event_date": (current_time - millis_in_10_minutes)},
                {"event_id": 3000, "event_date": (current_time - millis_in_an_hour)},
                {"event_id": 4000, "event_date": (current_time + millis_in_5_minutes)},
                {"event_id": 5000, "event_date": (current_time + millis_in_10_minutes)},
                {"event_id": 6000, "event_date": (current_time + millis_in_an_hour)},
                {"event_id": 7000, "event_date": (current_time + millis_in_10_minutes)},
            ]
        )
        expect = [5000, 6000]
        result = filter_no_schedule_events_in_mongo(
            recommendation_list=self.recommendation_list,
            db_connection=rec_db_conn,
            return_number=2,
            event_id_str="event_id",
            event_date_str="event_date",
            no_schedule_table_name="test_col",
            schedule_time_buffer=millis_in_7_minutes,
        )
        client.drop_database("test")
        assert operator.eq(expect, result)


if __name__ == "__main__":
    pytest.main()
