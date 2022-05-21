import json
import urllib
from unittest.mock import patch

import datetime
import pytest
import pickle
from app.main.util.controller_args import b2b_args
from app.main.util.global_db_connection import redis_client
from app.main import create_app, glb_db_conn
from app.main.util.test_connection import (
    create_connection,
    disconnection,
    create_local_connection,
    disconnect_local_connection,
    create_fake_redis_connection,
)


@pytest.fixture(scope="module", autouse=True)
def app_test_client():
    """
    An arrange fixture used to setup the flask app test client
    """
    with create_app(config_name="test").test_client() as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def mongo_client():
    """
    An arrange fixture for connection and disconnection to mongo test client
    """
    connection = create_connection()
    yield connection
    disconnection(connection)


@pytest.fixture(scope="module")
def fake_redis_client():
    """
    https://stackoverflow.com/questions/62916820/how-to-get-pytest-fixture-return-value-in-autouse-mode
    Since we are using app.main.util.connection for redis_client because it gets fake_redis_connection for pytest we don't need this
    An arrange fixture for connection to redis test client
    """
    with create_fake_redis_connection() as fake_redis_client:
        # add items to redis
        yield fake_redis_client
        # delete items


@pytest.fixture(scope="function")
def mock_filter_archived_events_in_mongo():
    """
    An arrange fixture used to mock mongo archived events client
    """
    with patch(
        "app.main.service.michaels_service.filter_archived_events_in_mongo",
        autospec=True,
    ) as mock_michaels_mongo_archived_events_client, patch(
        "app.main.service.mktplace_service.filter_archived_events_in_mongo",
        autospec=True,
    ) as mock_mktplace_mongo_archived_events_client:
        mock_michaels_mongo_archived_events_client.return_value = ["1", "2", "3"]
        mock_mktplace_mongo_archived_events_client.return_value = ["1", "2", "3"]
        yield


@pytest.fixture(scope="function")
def mock_filter_no_schedule_events_in_mongo():
    """
    An arrange fixture used to mock mongo no filter schedule events client
    """
    with patch(
        "app.main.service.michaels_service.filter_no_schedule_events_in_mongo",
        autospec=True,
    ) as mock_michaels_mongo_filter_no_schedule_client, patch(
        "app.main.service.mktplace_service.filter_no_schedule_events_in_mongo",
        autospec=True,
    ) as mock_mktplace_mongo_filter_no_schedule_client:
        mock_michaels_mongo_filter_no_schedule_client.return_value = ["1", "2", "3"]
        mock_mktplace_mongo_filter_no_schedule_client.return_value = ["1", "2", "3"]
        yield


@pytest.fixture(scope="function", autouse=True)
def mongo_filter_inactive_item_list():
    """
    An arrange fixture used to create filter inactive item list on mongo
    """
    local_conn, local_col = create_local_connection()  # connection created
    local_col.insert_many(
        [
            {"item_number": "1", "status": 1},
            {"item_number": "2", "status": 1},
            {"item_number": "3", "status": 0},
            {"item_number": "4", "status": 1},
            {"item_number": "5", "status": 0},
            {"item_number": "6", "status": 0},
            {"item_number": "7", "status": 1},
            {"item_number": "8", "status": 1},
            {"item_number": "9", "status": 1},
        ]
    )
    yield local_conn, local_col
    disconnect_local_connection(local_conn)  # disconnect connection


@pytest.fixture(scope="function")
def mongo_filter_item_with_badge():
    """
    An arrange fixture used to create filter item with time badges
    """
    current_time = datetime.datetime.utcnow()
    item_with_badges_1 = {
        "item_number": "item101",
        "status": 1,
        "badges": {
            "badges_check_name": True,
            "badges_start_date_name": (current_time - datetime.timedelta(days=3)),
            "badges_expiration_date_name": (current_time + datetime.timedelta(days=3)),
        },
    }
    item_with_badges_2 = {
        "item_number": "item102",
        "status": 0,
        "badges": {
            "badges_check_name": False,
            "badges_start_date_name": (current_time - datetime.timedelta(days=3)),
            "badges_expiration_date_name": (current_time + datetime.timedelta(days=1)),
        },
    }
    item_with_badges_3 = {
        "item_number": "item103",
        "status": 1,
        "badges": {
            "badges_check_name": True,
            "badges_start_date_name": (current_time - datetime.timedelta(days=3)),
            "badges_expiration_date_name": (current_time + datetime.timedelta(days=3)),
        },
    }
    item_with_badges_4 = {
        "item_number": "item104",
        "status": 1,
        "badges": {
            "badges_check_name": True,
            "badges_start_date_name": (current_time - datetime.timedelta(days=5)),
            "badges_expiration_date_name": (current_time - datetime.timedelta(days=3)),
        },
    }
    local_conn, local_col = create_local_connection()
    local_col.insert_many(
        [
            item_with_badges_1,
            item_with_badges_2,
            item_with_badges_3,
            item_with_badges_4,
        ]
    )
    yield local_conn, local_col
    disconnect_local_connection(local_conn)  # disconnect connection


@pytest.fixture(scope="function")
def mongo_insert_items_list():
    """
    An arrange fixture used to insert item, recommendations and score with default collection name
    """
    local_conn1, local_col1 = create_local_connection(
        db_name="test", collection_name="test_collection"
    )
    local_col1.insert_many(
        [
            {
                "item_id": "1001",
                "recommendations": ["1", "2", "3"],
                "score": [1, 2, 3],
            },
            {
                "item_id": "1002",
                "recommendations": ["1", "2", "3"],
                "score": [1, 2, 3],
            },
            {
                "item_id": "1003",
                "recommendations": ["1", "2", "6"],
                "score": [1, 2, 3],
            },
        ]
    )
    yield local_conn1, local_col1
    disconnect_local_connection(local_conn1)  # disconnect connection


@pytest.fixture(scope="module")
def mock_redis_client(request):
    """
    An arrange fixture used to mock redis client
    """
    with patch(
        "app.main.service.michaels_service.rec_api_redis_client", autospec=True
    ) as mock_michaels_redis_client, patch(
        "app.main.service.b2b_edu_service.rec_api_redis_client", autospec=True
    ) as mock_b2b_edu_redis_client, patch(
        "app.main.service.b2b_ent_service.rec_api_redis_client", autospec=True
    ) as mock_b2b_ent_redis_client, patch(
        "app.main.service.mktplace_service.rec_api_redis_client", autospec=True
    ) as mock_mktplace_redis_client:
        if request.param:
            mock_michaels_redis_client.hget.return_value = json.dumps(request.param)
            mock_b2b_edu_redis_client.hget.return_value = json.dumps(request.param)
            mock_b2b_ent_redis_client.hget.return_value = json.dumps(request.param)
            mock_mktplace_redis_client.hget.return_value = json.dumps(request.param)
        else:
            mock_michaels_redis_client.hget.return_value = request.param
            mock_b2b_edu_redis_client.hget.return_value = request.param
            mock_b2b_ent_redis_client.hget.return_value = request.param
            mock_mktplace_redis_client.hget.return_value = request.param
        yield


@pytest.fixture(scope="function")
def mongo_filter_inactive_item_with_collection_name(request):
    """
    An arrange fixture used to create filter inactive item list on mongo with collection name
    """

    if request.param:
        local_conn, local_col = create_local_connection(collection_name=request.param)
    else:
        local_conn, local_col = create_local_connection()

    local_col.insert_many(
        [
            {"item_number": "1", "status": 1},
            {"item_number": "2", "status": 1},
            {"item_number": "3", "status": 0},
            {"item_number": "4", "status": 1},
            {"item_number": "5", "status": 0},
            {"item_number": "6", "status": 0},
            {"item_number": "7", "status": 1},
            {"item_number": "8", "status": 1},
            {"item_number": "9", "status": 1},
        ]
    )
    yield local_conn, local_col
    disconnect_local_connection(local_conn)  # disconnect connection


@pytest.fixture(scope="function")
def mongo_filter_inactive_category(request):
    """
    An arrange fixture used to create filter inactive item list on mongo
    """
    local_conn, local_col = create_local_connection(
        collection_name=request.param
    )  # connection created
    local_col.insert_many(
        [
            {
                "category_path": "root//ABC",
                "recommendations": ["1", "3", "4"],
                "score": [6, 5, 4],
            },
            {
                "category_path": "root//DEF",
                "recommendations": ["2", "6", "7"],
                "score": [6, 5, 4],
            },
            {
                "category_path": "root//GHI",
                "recommendations": [
                    "3",
                    "5",
                    "6",
                ],  # inactive recommendations in this category
                "score": [6, 5, 4],
            },
            {
                "category_path": "root//JKL",
                "recommendations": ["7", "8", "9"],
                "score": [6, 5, 4],
            },
        ]
    )
    yield local_conn, local_col
    disconnect_local_connection(local_conn)  # disconnect connection


@pytest.fixture(scope="function")
def mongo_similar_items_by_popularity(request):
    """
    An arrange fixture used to create similar_items_by_popularity data on mongo and redis
    """
    local_conn, local_col = create_local_connection(collection_name=request.param)
    local_col.insert_many(
        [
            {"item_id": "1", "score": 6},
            {"item_id": "2", "score": 5},
            {"item_id": "3", "score": 5},
            {"item_id": "4", "score": 7},
            {"item_id": "5", "score": 3},
            {"item_id": "6", "score": 1},
        ]
    )
    yield local_conn, local_col
    disconnect_local_connection(local_conn)  # disconnect connection


@pytest.fixture(scope="function")
def mongo_filter_scored_item_with_collection_name(request):
    """
    An arrange fixture used to create filter inactive item list on mongo
    """
    local_conn, local_col = create_local_connection(collection_name=request.param)
    local_col.insert_many(
        [
            {
                "item_id": "101",
                "recommendations": ["1", "2", "3"],
                "score": [6, 5, 4],
            },
            {
                "item_id": "102",
                "recommendations": ["2", "3", "4"],
                "score": [5, 4, 3],
            },
            {
                "item_id": "103",
                "recommendations": ["1", "2", "3"],
                "score": [1, 2, 3],
            },
            {
                "item_id": "104",
                "recommendations": ["1", "2", "3"],
                "score": [1, 2, 3],
            },
            {
                "item_id": "105",
                "recommendations": ["1", "2", "3"],
                "score": [1, 2, 3],
            },
        ]
    )
    yield local_conn, local_col
    disconnect_local_connection(local_conn)


@pytest.fixture(scope="function")
def redis_similar_items(request):
    redis_similar_items_hkey = request.param
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
    yield
    redis_client.delete(redis_similar_items_hkey)


@pytest.fixture(scope="function")
def redis_search_rerank():
    redis_hash_key = b2b_args["search_rerank_args"]["redis_hash_key"]["default"]
    redis_client.hmset(
        redis_hash_key,
        {
            "1011": pickle.dumps([1, 0, 0, 1, 0, 1, 1, 1, 0, 0]),
            "1022": pickle.dumps([1, 1, 1, 1, 0, 1, 0, 0, 1, 0]),
            "1033": pickle.dumps([0, 1, 0, 0, 1, 0, 0, 1, 1, 0]),
            "1044": pickle.dumps([1, 1, 0, 0, 1, 0, 1, 1, 1, 0]),
            "1088": pickle.dumps([]),
            "1099": pickle.dumps([]),
        },
    )
    yield
    redis_client.delete(redis_hash_key)


@pytest.fixture(scope="function")
def mongo_related_category():
    local_conn, local_col = create_local_connection(collection_name="test_sch")
    local_col.insert_many(
        [
            {"category": "category1", "image_url": "image1"},
            {"category": "category2", "image_url": "image2"},
            {"category": "category3", "image_url": "image3"},
        ]
    )
    yield
    disconnect_local_connection(local_conn)


def pytest_configure():
    pytest.test_pfe = "test_pfe"
    pytest.test_tp = "test_tp"
    pytest.test_pab = "test_pab"
    # service var
    pytest.filter_args = {
        "table_name": "test_col",
        "item_col_name": "item_number",
        "check_col_name": "status",
        "check_val": 1,
        "db_connection": glb_db_conn,
    }
    pytest.project_filter_args = {
        "project_table_name": "test_col",
        "project_item_col_name": "item_number",
        "project_check_col_name": "status",
        "project_check_val": 1,
        "db_connection": glb_db_conn,
    }
    # service var ends

    # controller var
    pytest.filter_url_string = urllib.parse.urlencode(
        {
            "db_name": "test_db",
            "table_name": "test_col",
            "item_col_name": "item_number",
            "check_col_name": "status",
            "check_val": 1,
        },
        doseq=True,
    )
    pytest.project_filter_url_string = urllib.parse.urlencode(
        {
            "project_db_name": "test_db",
            "project_table_name": "test_col",
            "project_item_col_name": "item_number",
            "project_check_col_name": "status",
            "project_check_val": 1,
        },
        doseq=True,
    )
    pytest.filter_archive_url_string = urllib.parse.urlencode(
        {
            "event_id_str": "event_id",
            "event_type_str": "event_type",
            "archived_str": "archived",
            "archived_event_table_name": "table",
        },
        doseq=True,
    )
    pytest.filter_badges_url_string = urllib.parse.urlencode(
        {
            "badges_name": "badges",
            "badges_check_name": "badges_check_name",
            "badges_check_val": True,
            "badges_start_date_name": "badges_start_date_name",
            "badges_expiration_date_name": "badges_expiration_date_name",
        },
        doseq=True,
    )
    pytest.similar_items_for_bundle_args_url_string = urllib.parse.urlencode(
        {
            "collection_name": "test_collection",
            "candidate_count": 3,
        },
        doseq=True,
    )
    pytest.generate_categories_args_url_string = urllib.parse.urlencode(
        {"search_term": "paint", "candidate_count": 1, "word_vector_length": 4},
        doseq=True,
    )

    now = datetime.date.today()
    pytest.recently_view_redis_data = {
        "view_list": ["1", "2", "3", "4"],
        "view_time": [
            (now - datetime.timedelta(days=2)).__format__("%Y-%m-%d")
            + "T17:41:45.919Z",
            (now - datetime.timedelta(days=4)).__format__("%Y-%m-%d")
            + "T17:41:43.304Z",
            (now - datetime.timedelta(days=30)).__format__("%Y-%m-%d")
            + "T16:58:27.602Z",
            (now - datetime.timedelta(days=50)).__format__("%Y-%m-%d")
            + "T16:58:15.932Z",
        ],
    }
    # controller var ends

    redis_hash_key = b2b_args["search_rerank_args"]["redis_hash_key"]["default"]
    pytest.search_rerank_data = [
        {
            "items_id_list": "1011 1022",
            "order_history_list": "1033",
            "order_history_weights": "1",
            "redis_hash_key": redis_hash_key,
        },
        {
            "items_id_list": "1011 1022",
            "order_history_list": "1033 1044",
            "order_history_weights": "1 2",
            "redis_hash_key": redis_hash_key,
        },
        {
            "items_id_list": "1011 1022",
            "order_history_list": "1055 1066",
            "order_history_weights": "1 2",
            "redis_hash_key": redis_hash_key,
        },
        {
            "items_id_list": "1066 1077",
            "order_history_list": "1089 1078",
            "order_history_weights": "1 2",
            "redis_hash_key": redis_hash_key,
        },
        {
            "items_id_list": "1088 1099",
            "order_history_list": "1089",
            "order_history_weights": "1 2",
            "redis_hash_key": redis_hash_key,
        },
        {
            "items_id_list": "1088 1099",
            "order_history_list": "1089 1099",
            "order_history_weights": "1 2",
            "redis_hash_key": redis_hash_key,
        },
    ]
