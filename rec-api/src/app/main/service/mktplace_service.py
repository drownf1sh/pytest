import json

import time

from flask import abort
from mongoengine import DoesNotExist

from app.main.database.cache import cache
from app.main.model.mktplace import (
    ItemSimilarity,
    TrendingNowModel,
    UserDefTrendingNow,
    PopularEvent,
    PopularProject,
    PopularSearchKeyword,
    YouMayAlsoBuy,
    EventForYou,
    PopularProductsInProjects,
    YesterdayPopularItem,
    NewProjects,
    PopularFirstLayerCategory,
    FavoriteItem,
    ShopNearYou,
    UpcomingEvent,
    TrendingEvent,
    PopularVisitedEvents,
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
from app.main.model.mktplace import PopularItem
from app.main.model.mktplace import UserRecommend
from app.main.model.mktplace import RecForYouSearch
from app.main.util.filter_archived_events import (
    filter_archived_events_in_mongo,
    filter_no_schedule_events_in_mongo,
)
from app.main.util.filter_deactivated_items import filter_deactivated_items
from app.main.util.general_service_functions import (
    filter_recently_view_streaming_based_on_time,
    search_people_also_buy,
    search_rerank,
    get_trending_now_all_category,
    get_similar_items,
    get_purchased_together_for_bundle,
    get_top_picks,
    get_shopping_cart_bundle,
    rank_similar_items_by_popularity_score,
    get_picks_from_experts,
)
from app.main.util.generate_categories import generate_categories
from app.main import glb_db_conn, rec_db_conn
from app.main.util.rec_api_redis_client import rec_api_redis_client


# from app.main.configuration.vault_vars_config import RECENTLY_VIEW_DB
CACHE_TIMEOUT = 300


def get_mktplace_recommended_for_you(**kwargs):
    """
    Search the database to get recommend for you data by given user id
    and return results with number of given candidate count
    :param user_id: str
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    user_id = kwargs["user_id"]
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }

    try:
        recommend_for_you_object = UserRecommend.objects(user_id=user_id).get()
    except DoesNotExist:
        return get_mktplace_popular_item(candidate_count=candidate_count, **filter_args)
    return filter_deactivated_items(
        recommendation_list=recommend_for_you_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_similar_items", query_string=True
)
def get_mktplace_similar_items(**kwargs):
    """
    Search the database to get similar item data by given target item
    :param item_id: str. Item ID
    :param filter_args: dict. The arguments for filtering out inactive items
    :param candidate_count: int. The count of recommended non-ad items
    # :param ad_candidate_count: int. The count of recommended ad items
    :param redis_similar_items_hash_key: str. The redis hash key for similar_items
    # :param redis_similar_ad_items_hash_key: str. The redis hash key for similar_ad_items
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    return get_similar_items(ItemSimilarity, **kwargs)


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_popular_item", query_string=True
)
def get_mktplace_popular_item(**kwargs):
    """
    Search the database to get popular item data with number of candidate count
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        popular_item_object = PopularItem.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e
    return filter_deactivated_items(
        recommendation_list=popular_item_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def get_search_term_categories(**kwargs):
    """Get suggested categories for search terms. This service is different with others
    because of its logic and usage.

    :param kwargs:
    search_term: str
    The search_term used to get categories

    candidate_count: int, default=5
    The amount of suggested categories will be returned.

    word_vector_length: int
    The vector's dimension for word_embedding. Currently it's 300 dimensions for dev/prod
    and 4 dimensions for pytest.

    :return:
    List of suggested categories

    """
    search_term_cat_args = {
        "search_term": kwargs["search_term"],
        "candidate_count": kwargs["candidate_count"],
        "word_vector_length": kwargs["word_vector_length"],
    }

    return generate_categories(**search_term_cat_args)


# def put_mktplace_similar_items(**kwargs):
#     # Get item from glb database
#     sku_number = kwargs["sku_number"]
#     collection_name = kwargs["collection_name"]
#     candidate_count = kwargs["candidate_count"]
#     item = glb_db_conn.get_database_instance()[collection_name].find_one(
#         {"sku_number": sku_number}
#     )
#     try:
#         # Get item info
#         consumer_friendly_description = item["consumer_friendly_description"]
#         full_taxonomy_path = item["full_taxonomy_path"]
#         df_item_info = pd.DataFrame(
#             {
#                 "sku_number": [sku_number],
#                 "consumer_friendly_description": [consumer_friendly_description],
#                 "category_path": [full_taxonomy_path],
#             }
#         )
#         # Run the streaming_cbf pipeline to get similar items
#         result = cbf_pipeline.predict(
#             df_item_info,
#             candidate_count=candidate_count,
#         )
#         # Save data into ItemSimilarity collection
#         ItemSimilarity.objects(item_id=sku_number).update_one(
#             set__recommendations=result[0]["recommendations"], upsert=True
#         )
#         return result
#     except TypeError:
#         # If item doesn't exist in glb db, raise DoesNotExit error
#         print("sku number does not exist in glb database")
#         raise DoesNotExist


# def get_mktplace_recently_viewed(**kwargs):
#     """
#     Search the MySQL database to get recently viewed data
#     by user id and get the result with number of candidate count
#     :param user_id: str
#     :param candidate_count: int
#     Filter params to remove inactive items
#     :param table_name: str. The name of target table to be searched
#     :param item_col_name: str. Based on specific column to search
#     :param check_col_name: str. Based on specific column to check val
#     :param check_val: str. The value to be checked
#     :param db_connection: Given db connection to do filtering
#     :return: a recommendation list
#     """
#     user_id = kwargs["user_id"]
#     candidate_count = kwargs["candidate_count"]
#     filter_args = {
#         "table_name": kwargs["table_name"],
#         "item_col_name": kwargs["item_col_name"],
#         "check_col_name": kwargs["check_col_name"],
#         "check_val": kwargs["check_val"],
#         "db_connection": glb_db_conn,
#     }
#     # check if user exists or not
#     user_sql = (
#         f"SELECT user_id FROM `{RECENTLY_VIEW_DB}` "
#         f"WHERE user_id = '{user_id}' LIMIT 1"
#     )
#
#     user_res = (
#         bigquery_client.query(user_sql).result().to_dataframe()["user_id"].tolist()
#     )
#     if len(user_res) == 0:
#         raise DoesNotExist
#
#     sql = (
#         f"SELECT unstruct_event_com_michaels_item_view_1_0_0.item_id "
#         f"FROM `{RECENTLY_VIEW_DB}` "
#         f"WHERE event_name='page_view' AND app_id = 'mik-web' AND user_id = '{user_id}' "
#         f"AND Date(collector_tstamp) BETWEEN DATE_SUB(current_date(), INTERVAL 7 DAY) AND current_date() "
#         f"AND unstruct_event_com_michaels_item_view_1_0_0.item_id NOT IN ("
#         f"SELECT DISTINCT unstruct_event_com_michaels_add_to_cart_1_0_0.item_id "
#         f"FROM `{RECENTLY_VIEW_DB}` "
#         f"WHERE user_id = '{user_id}' AND event_name = 'add_to_cart' AND app_id = 'mik-web' "
#         f"AND Date(collector_tstamp) BETWEEN DATE_SUB(current_date(), INTERVAL 7 DAY) AND current_date()) "
#         f"GROUP BY unstruct_event_com_michaels_item_view_1_0_0.item_id "
#         f"ORDER BY MAX(collector_tstamp) DESC LIMIT {candidate_count};"
#     )
#
#     res = bigquery_client.query(sql).result().to_dataframe()["item_id"].tolist()
#     active_items = filter_deactivated_items(
#         recommendation_list=res,
#         return_number=candidate_count,
#         **filter_args,
#     )


def get_mktplace_recently_viewed_streaming(**kwargs):
    """
    Search the redis database to get recently viewed data
    by user id and get the result with number of candidate count
    :param user_id: str
    :param date_interval: int
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    redis_hkey = "fgm_streaming_recently_view"
    user_id = kwargs["user_id"]
    # get data from redis by given user_id
    data = rec_api_redis_client.hget(redis_hkey, user_id)
    # # raise 404 if user id not found
    if data is None:
        return []
    return filter_recently_view_streaming_based_on_time(data=data, **kwargs)


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="mktplace_search_people_also_buy",
    query_string=True,
)
def get_mktplace_search_people_also_buy(**kwargs):
    """
    Provides recommendation services using item ids and scores for mktplace search_people_also_buy
    :param items_id_list: str. The list of item IDs. Separated by space.
    :param items_scores: str. The scores corresponding to the items. Separated by space.
    :param collection_name: str. The mongodb collection to access documents
    :param candidate_count: int. No. of recommended items, default 5
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    return search_people_also_buy(**kwargs)


def get_mktplace_rec_for_you_search(**kwargs):
    """
    Search the database to get list of recommended search terms by user id
    and get the result with number of candidate count
    :param user_id: int
    :param candidate_count: int
    :return: a recommendation list
    """
    user_id = kwargs["user_id"]
    candidate_count = kwargs["candidate_count"]

    try:
        rec_for_you_search_object = RecForYouSearch.objects(user_id=user_id).get()
    except DoesNotExist:
        return get_mktplace_popular_search_keyword(candidate_count=candidate_count)
    return rec_for_you_search_object.recommendations[:candidate_count]


def post_mktplace_search_rerank(json_dict):
    """
    Reranks the search with the weighted sum of similarity score between order history and search history
    :param json_dict: Consists of items_id_list, order_history_list and order_history_weights

    :return: List of reranked search results with score
    """
    if "order_history_weights" in json_dict:
        order_history_weights = json_dict["order_history_weights"]
    else:
        order_history_weights = ""
    if "redis_hash_key" in json_dict:
        redis_hash_key = json_dict["redis_hash_key"]
    else:
        redis_hash_key = "cbf_item_vector"
    items_id_list = json_dict["items_id_list"]
    order_history_list = json_dict["order_history_list"]

    return search_rerank(
        items_id_list, order_history_list, redis_hash_key, order_history_weights
    )


def put_mktplace_user_defined_trending_now(**kwargs):
    """
    Adds a list of user defined trending now recommended items for a given category path to the mongo collection
    :param category_path: str Category path for the items trending now to be added
    :param rec_item_ids: str Space separated recommended item ids to be added
    :return The resulting document that was added to the collection
    """
    category_path = kwargs["category_path"]
    if not kwargs["rec_item_ids"]:
        rec_item_ids = []
    else:
        rec_item_ids = kwargs["rec_item_ids"].strip().split(",")

    # Save data into user_defined_trending_now collection
    UserDefTrendingNow.objects(category_path=category_path).update(
        set__recommendations=rec_item_ids, upsert=True
    )
    # Storing the inserted or updated document as a dict for response
    result = {
        "category_path": category_path,
        "recommendations": UserDefTrendingNow.objects(category_path=category_path)
        .get()
        .recommendations,
    }
    return result


def get_mktplace_user_defined_trending_now(**kwargs):
    """
    Search the database to get user defined trending now data by category path
    and get the result with number of candidate count
    :param category_path: str
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    category_path = kwargs["category_path"]
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        user_def_tn_object = UserDefTrendingNow.objects(
            category_path=category_path
        ).get()
    except DoesNotExist:
        return []
    return filter_deactivated_items(
        recommendation_list=user_def_tn_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def get_mktplace_trending_now_model(**kwargs):
    """
    Search the database to get trending now data by category path
    and get the result with number of candidate count
    :param category_path: str
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    category_path = kwargs["category_path"]
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        model_tn_object = TrendingNowModel.objects(category_path=category_path).get()
    except DoesNotExist:
        return []
    return filter_deactivated_items(
        recommendation_list=model_tn_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_trending_now", query_string=True
)
def get_mktplace_trending_now(**kwargs):
    """
    Search the database to get user defined trending now data and trending now model by category path
    and get the result with number of candidate count
    :param category_path: str
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    category_path = kwargs["category_path"]
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    user_def_tn = get_mktplace_user_defined_trending_now(
        category_path=category_path,
        candidate_count=candidate_count,
        **filter_args,
    )
    tn_model = get_mktplace_trending_now_model(
        category_path=category_path,
        candidate_count=candidate_count,
        **filter_args,
    )
    if user_def_tn:
        return user_def_tn
    elif tn_model:
        return tn_model
    else:
        return []


def get_mktplace_trending_now_all_category(**kwargs):
    """
    Get category paths along with the required number of recommendations from user defined trending now
    or with trending now model
    :param user_defined_trending_now: The MongoDB Collection for user defined trending now model
    :param trending_now: The MongoDB Collection for trending now model
    :param candidate_count: The count of recommendations that need to returned for each category path
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    """
    return get_trending_now_all_category(**kwargs)


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_popular_event", query_string=True
)
def get_mktplace_popular_event(**kwargs):
    """
    Search the database to get popular event data with number of candidate count
    :param candidate_count: int
    :param event_type: str

    Parameters used to filter archived events
    :param event_id: str
        string "event_id" used to filter in a db document
    :param event_type: str
        string "event_type" used to filter in a db document
    :param archived: str
        string "archived" used to filter in a db document
    :param archived_event_table_name: str
        table name used to search events results
    :return: a recommendation list
    """
    event_type = kwargs["event_type"]
    candidate_count = kwargs["candidate_count"]
    try:
        popular_event_object = PopularEvent.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e
    active_events = filter_archived_events_in_mongo(
        recommendation_list=popular_event_object.recommendations,
        event_type_col=event_type,
        return_number=len(popular_event_object.recommendations),
        db_connection=rec_db_conn,
        **kwargs,
    )
    return filter_no_schedule_events_in_mongo(
        recommendation_list=active_events,
        return_number=candidate_count,
        db_connection=rec_db_conn,
        **kwargs,
    )


def get_mktplace_shop_near_you(**kwargs):
    """
    Recommends the shops near you using zip code
    :param zip_code: int
    :param candidate_count: int
    :return: a recommendation list
    """
    zip_code = kwargs["zip_code"]
    candidate_count = kwargs["candidate_count"]
    try:
        shop_near_you_object = ShopNearYou.objects(zip_code=zip_code).get()
    except DoesNotExist:
        return []
    return shop_near_you_object.recommendations[:candidate_count]


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_popular_project", query_string=True
)
def get_mktplace_popular_project(**kwargs):
    """
    Search the database to get popular project data with number of candidate count
    :param candidate_count: int
    Filter params to remove inactive projects
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    candidate_count = kwargs["candidate_count"]
    project_filter_args = {
        "table_name": kwargs["project_table_name"],
        "item_col_name": kwargs["project_item_col_name"],
        "check_col_name": kwargs["project_check_col_name"],
        "check_val": kwargs["project_check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        popular_project_object = PopularProject.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e
    active_projects = filter_deactivated_items(
        recommendation_list=popular_project_object.recommendations,
        return_number=candidate_count,
        **project_filter_args,
    )
    return active_projects[:candidate_count]


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_trending_project", query_string=True
)
def get_mktplace_trending_project(**kwargs):
    """
    Search the database to get trending project data with number of candidate count
    :param candidate_count: int
    Filter params to remove inactive projects
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    candidate_count = kwargs["candidate_count"]
    project_filter_args = {
        "table_name": kwargs["project_table_name"],
        "item_col_name": kwargs["project_item_col_name"],
        "check_col_name": kwargs["project_check_col_name"],
        "check_val": kwargs["project_check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        trending_project_object = TrendingProject.objects(group_id=0).get()
    except DoesNotExist:
        return []
    return filter_deactivated_items(
        recommendation_list=trending_project_object.recommendations,
        return_number=candidate_count,
        **project_filter_args,
    )


def get_mktplace_you_may_also_buy(**kwargs):
    """
    Search the database to get popular project data with number of candidate count
    :param user_id: str
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    user_id = kwargs["user_id"]
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }

    try:
        you_may_also_buy_object = YouMayAlsoBuy.objects(user_id=user_id).get()
    except DoesNotExist:
        return get_mktplace_popular_item(**kwargs)
    return filter_deactivated_items(
        recommendation_list=you_may_also_buy_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def get_mktplace_top_picks(**kwargs):
    """
    This service gets the top picks for the user in each category
    Then we fetch k recommendations for user_id from streaming_top_picks in Redis
    If that doesn't exist then get top k categories from fgm_popular_first_layer_category in mongo
    then use these categories to get 1 recommendation from the fgm_popular_item_by_category mongo collection

    :param user_id: int. If login, we will input a user_id
    :param candidate_count: int. No. of recommended items, default 5
    :param redis_hash_key: str. redis hash key for streaming top picks
    :param collection_name: str. mongo collection for popular_item_by_category
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return a recommendation list
    """
    return get_top_picks(PopularFirstLayerCategory, **kwargs)


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="mktplace_popular_search_keyword",
    query_string=True,
)
def get_mktplace_popular_search_keyword(**kwargs):
    """
    Fetches the popular search keyword recommendations with number of candidate count
    :param candidate_count: int
    :return: a recommendation list
    """
    candidate_count = kwargs["candidate_count"]
    try:
        popular_search_keyword_object = PopularSearchKeyword.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e
    return popular_search_keyword_object.recommendations[:candidate_count]


def get_mktplace_event_for_you(**kwargs):
    """
    Search the database to get event for you data by given user id
    and return results with number of given candidate count
    :param user_id: str
    :param candidate_count: int
    :param event_type: str

    Parameters used to filter archived events
    :param event_id: str
        string "event_id" used to filter in a db document
    :param event_type: str
        string "event_type" used to filter in a db document
    :param archived: str
        string "archived" used to filter in a db document
    :param archived_event_table_name: str
        table name used to search events results
    :return: a recommendation list
    """
    user_id = kwargs["user_id"]
    event_type = kwargs["event_type"]
    candidate_count = kwargs["candidate_count"]
    try:
        event_for_you_object = EventForYou.objects(user_id=user_id).get()
    except DoesNotExist:
        return get_mktplace_popular_event(
            **kwargs,
        )
    active_events = filter_archived_events_in_mongo(
        recommendation_list=event_for_you_object.recommendations,
        event_type_col=event_type,
        return_number=len(event_for_you_object.recommendations),
        db_connection=rec_db_conn,
        **kwargs,
    )
    return filter_no_schedule_events_in_mongo(
        recommendation_list=active_events,
        return_number=candidate_count,
        db_connection=rec_db_conn,
        **kwargs,
    )


def get_mktplace_purchased_together_bundle(**kwargs):
    """
    Search the database to get purchase together data by given item id list
    and get the result with number of candidate count
    :param items_id_list: list
    :param candidate_count: int
    :param collection_name: str
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: recommendations list
    """
    items_ids_list = kwargs["items_id_list"].strip().split(" ")
    candidate_count = kwargs["candidate_count"]
    collection_name = kwargs["collection_name"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    result = get_purchased_together_for_bundle(items_ids_list, collection_name)
    return filter_deactivated_items(
        recommendation_list=result,
        return_number=candidate_count,
        **filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="mktplace_popular_products_in_projects",
    query_string=True,
)
def get_mktplace_popular_products_in_projects(**kwargs):
    """
    Search the database to get popular products in projects with number of candidate count
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }

    try:
        popular_products_in_projects = PopularProductsInProjects.objects(
            group_id=0
        ).get()
    except DoesNotExist as e:
        raise e
    return filter_deactivated_items(
        recommendation_list=popular_products_in_projects.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="mktplace_yesterday_popular_item",
    query_string=True,
)
def get_mktplace_yesterday_popular_item(**kwargs):
    """
    Search the database to get fgm yesterday popular item data with number of candidate count
    :param candidate_count: int
    :return: a recommendation list of fgm_yesterday_popular_item
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    """
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        yesterday_popular_item_object = YesterdayPopularItem.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e
    return filter_deactivated_items(
        recommendation_list=yesterday_popular_item_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_new_projects", query_string=True
)
def get_mktplace_new_projects(**kwargs):
    """
    Search the database to get new projects with number of candidate count
    :param candidate_count: int
    Filter params to remove inactive projects
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    candidate_count = kwargs["candidate_count"]
    project_filter_args = {
        "table_name": kwargs["project_table_name"],
        "item_col_name": kwargs["project_item_col_name"],
        "check_col_name": kwargs["project_check_col_name"],
        "check_val": kwargs["project_check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        new_projects_object = NewProjects.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e
    return filter_deactivated_items(
        recommendation_list=new_projects_object.recommendations,
        return_number=candidate_count,
        **project_filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_favorite_item", query_string=True
)
def get_mktplace_favorite_item(**kwargs):
    """
    Search the database to get fgm favorite item data with number of candidate count
    :param candidate_count: int
    :return: a recommendation list of fgm_favourite_item
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    """
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        favorite_item_object = FavoriteItem.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e
    return filter_deactivated_items(
        recommendation_list=favorite_item_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def get_mktplace_popular_item_by_store(**kwargs):
    """
    Search the database to get popular item data with number of candidate count
    :param store_id: int
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    store_id = kwargs["store_id"]
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }

    try:
        popular_item_object = PopularItemByStore.objects(store_id=store_id).get()
    except DoesNotExist:
        return []

    return filter_deactivated_items(
        recommendation_list=popular_item_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_upcoming_event", query_string=True
)
def get_mktplace_upcoming_event(**kwargs):
    """
    Search the database to get upcoming events id and schedules id with number of candidate count
    :param candidate_count: int
    :param event_type: str

    Parameters used to filter archived events
    :param event_id: str
        string "event_id" used to filter in a db document
    :param event_type: str
        string "event_type" used to filter in a db document
    :param archived: str
        string "archived" used to filter in a db document
    :param archived_event_table_name: str
        table name used to search events results
    :return: a dict with event id list and schedules id list
    """
    event_type = kwargs["event_type"]
    candidate_count = kwargs["candidate_count"]
    query_timestamp = int(time.time()) % (24 * 3600) // 900 * 900

    try:
        upcoming_event = UpcomingEvent.objects(timestamp=query_timestamp).get()
    except DoesNotExist as e:
        raise e
    active_events = filter_archived_events_in_mongo(
        recommendation_list=upcoming_event.events_id,
        event_type_col=event_type,
        return_number=len(upcoming_event.events_id),
        db_connection=rec_db_conn,
        **kwargs,
    )
    filtered_events = filter_no_schedule_events_in_mongo(
        recommendation_list=active_events,
        return_number=candidate_count,
        db_connection=rec_db_conn,
        **kwargs,
    )
    filtered_indexes = [upcoming_event.events_id.index(x) for x in filtered_events]
    filtered_schedules = [upcoming_event.schedules_id[i] for i in filtered_indexes]
    result = {
        "event_id": filtered_events,
        "schedules_id": filtered_schedules,
    }
    return [result]


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_trending_event", query_string=True
)
def get_mktplace_trending_event(**kwargs):
    """
    Search the database to get fgm trending event data with number of candidate count
    :param event_type: str
    :param candidate_count: int

    Parameters used to filter archived events
    :param event_id: str
        string "event_id" used to filter in a db document
    :param event_type: str
        string "event_type" used to filter in a db document
    :param archived: str
        string "archived" used to filter in a db document
    :param archived_event_table_name: str
        table name used to search events results
    :return: a recommendation list
    """
    event_type = kwargs["event_type"]
    candidate_count = kwargs["candidate_count"]
    try:
        trending_event_object = TrendingEvent.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e

    active_events = filter_archived_events_in_mongo(
        recommendation_list=trending_event_object.recommendations,
        event_type_col=event_type,
        return_number=len(trending_event_object.recommendations),
        db_connection=rec_db_conn,
        **kwargs,
    )
    return filter_no_schedule_events_in_mongo(
        recommendation_list=active_events,
        return_number=candidate_count,
        db_connection=rec_db_conn,
        **kwargs,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="mktplace_popular_visited_events",
    query_string=True,
)
def get_mktplace_popular_visited_events(**kwargs):
    """
    This service gets the popular visited events with number of candidate count.
    :param event_type: str
    :param candidate_count: int
    :param spanner_table_name: str. The google spanner table used to filter archived events

    Parameters used to filter archived events
    :param event_id: str
        string "event_id" used to filter in a db document
    :param event_type: str
        string "event_type" used to filter in a db document
    :param archived: str
        string "archived" used to filter in a db document
    :param archived_event_table_name: str
        table name used to search events results
    :return a recommendation list
    """
    event_type = kwargs["event_type"]
    candidate_count = kwargs["candidate_count"]
    try:
        popular_visited_events = PopularVisitedEvents.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e

    active_events = filter_archived_events_in_mongo(
        recommendation_list=popular_visited_events.recommendations,
        event_type_col=event_type,
        return_number=len(popular_visited_events.recommendations),
        db_connection=rec_db_conn,
        **kwargs,
    )
    return filter_no_schedule_events_in_mongo(
        recommendation_list=active_events,
        return_number=candidate_count,
        db_connection=rec_db_conn,
        **kwargs,
    )


def get_mktplace_streaming_trending_now_list(**kwargs):
    """
    Search redis fgm_streaming_trending_now_list
    with number of candidate count
    :param candidate_count: int
    :return: a recommendation list

    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering

    """
    candidate_count = kwargs["candidate_count"]
    redis_streaming_trending_now_list_key = kwargs[
        "redis_streaming_trending_now_list_key"
    ]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    redis_streaming_trending_now_list = rec_api_redis_client.get(
        redis_streaming_trending_now_list_key,
    )
    if redis_streaming_trending_now_list is None:
        abort(404)
    else:
        streaming_trending_now_list = json.loads(redis_streaming_trending_now_list)[
            "item_list"
        ]
        return filter_deactivated_items(
            recommendation_list=streaming_trending_now_list,
            return_number=candidate_count,
            **filter_args,
        )


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="mktplace_popular_first_layer_category",
    query_string=True,
)
def get_mktplace_popular_first_layer_category(**kwargs):
    """
    Search the database to get fgm popular_first_layer_category data with number of candidate count
    :param candidate_count: int
    :return a recommendation list
    """
    candidate_count = kwargs["candidate_count"]

    try:
        popular_first_layer_category = PopularFirstLayerCategory.objects(
            group_id=0
        ).get()
    except DoesNotExist as e:
        raise e

    return popular_first_layer_category.recommendations[:candidate_count]


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_people_also_buy", query_string=True
)
def get_mktplace_people_also_buy(**kwargs):
    """
    Search the database to get people also buy data by given item id
    and get the result with number of candidate count
    :param item_id: str
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    item_id = kwargs["item_id"]
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        people_also_buy_object = PeopleAlsoBuy.objects(item_id=item_id).get()
    except DoesNotExist:
        return []
    return filter_deactivated_items(
        recommendation_list=people_also_buy_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="mktplace_popular_visited_projects",
    query_string=True,
)
def get_mktplace_popular_visited_projects(**kwargs):
    """
    Search the database to get fgm popular_visited_projects data with number of candidate count
    :param candidate_count: int
    :return a recommendation list
    """
    candidate_count = kwargs["candidate_count"]

    try:
        popular_visited_projects = PopularVisitedProjects.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e

    return popular_visited_projects.recommendations[:candidate_count]


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="mktplace_popular_visited_items",
    query_string=True,
)
def get_mktplace_popular_visited_items(**kwargs):
    """
    Search the database to get fgm popular_visited_items data with number of candidate count
    :param candidate_count: int
    :return a recommendation list
    """
    candidate_count = kwargs["candidate_count"]

    try:
        popular_visited_items = PopularVisitedItems.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e

    return popular_visited_items.recommendations[:candidate_count]


def get_mktplace_shopping_cart_bundle(**kwargs):
    """
    Search redis and database to get fgm shopping cart bundle data with number of candidate count
    :param items_id_list: str. The bundle items ID list. Separated by space.
    :param candidate_count: int
    :param redis_similar_items_hash_key: str. Redis key for fgm_similar_items
    :param collection_name: str. fgm_purchased_together
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    return get_shopping_cart_bundle(**kwargs)


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="mktplace_popular_products_in_events",
    query_string=True,
)
def get_mktplace_popular_products_in_events(**kwargs):
    """
    Search the database to get fgm_popular_products_in_events data with number of candidate count
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }

    try:
        popular_products_in_events = PopularProductsInEvents.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e

    return filter_deactivated_items(
        recommendation_list=popular_products_in_events.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_similar_projects", query_string=True
)
def get_mktplace_similar_projects(**kwargs):
    """
    Search the database to get similar project data by given target project
    :param candidate_count: int
    :param external_id: str
    Filter params to remove inactive projects
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    external_id = kwargs["external_id"]
    candidate_count = kwargs["candidate_count"]
    project_filter_args = {
        "table_name": kwargs["project_table_name"],
        "item_col_name": kwargs["project_item_col_name"],
        "check_col_name": kwargs["project_check_col_name"],
        "check_val": kwargs["project_check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        similar_project_object = ProjectSimilarity.objects(
            external_id=external_id
        ).get()
    except DoesNotExist as e:
        raise e
    return filter_deactivated_items(
        recommendation_list=similar_project_object.recommendations,
        return_number=candidate_count,
        **project_filter_args,
    )


def get_mktplace_related_categories_by_category(**kwargs):
    """
    Search the database to get related categories data by category path
    and get the result with number of candidate count
    :param category_path: str
    :param candidate_count: int
    :return: a recommendation list
    """
    category_path = kwargs["category_path"]
    candidate_count = kwargs["candidate_count"]
    try:
        related_categories_by_category_object = RelatedCategoriesByCategory.objects(
            category_path=category_path
        ).get()
    except DoesNotExist:
        return []
    return related_categories_by_category_object.recommendations[:candidate_count]


def get_mktplace_popular_item_by_category(**kwargs):
    """
    Search the database to get popular item by category data with number of candidate count
    :param category_path: str
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    category_path = kwargs["category_path"]
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }

    try:
        popular_item_by_category_object = PopularItemByCategory.objects(
            category_path=category_path
        ).get()
    except DoesNotExist:
        return []

    return filter_deactivated_items(
        recommendation_list=popular_item_by_category_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="mktplace_similar_events", query_string=True
)
def get_mktplace_similar_events(**kwargs):
    """
    Search the database to get similar events data by given target event
    :param event_id: str
    :param event_type: str
    :param candidate_count: int

    Parameters used to filter archived events
    :param event_id: str
        string "event_id" used to filter in a db document
    :param event_type: str
        string "event_type" used to filter in a db document
    :param archived: str
        string "archived" used to filter in a db document
    :param archived_event_table_name: str
        table name used to search events results
    :return: a recommendation list
    """
    event_id = kwargs["event_id"]
    event_type = kwargs["event_type"]
    candidate_count = kwargs["candidate_count"]
    try:
        similar_event_object = SimilarEvents.objects(event_id=event_id).get()
    except DoesNotExist as e:
        raise e
    active_events = filter_archived_events_in_mongo(
        recommendation_list=similar_event_object.recommendations,
        event_type_col=event_type,
        return_number=len(similar_event_object.recommendations),
        db_connection=rec_db_conn,
        **kwargs,
    )
    return filter_no_schedule_events_in_mongo(
        recommendation_list=active_events,
        return_number=candidate_count,
        db_connection=rec_db_conn,
        **kwargs,
    )


def get_mktplace_similar_items_by_popularity(**kwargs):
    """
    Search the database to get a list of similar items given target item Id
    then order the results based on popularity score in fgm_popular_master_items database collection
    return a list of item with number of candidate count
    :param item_id: str. target item id
    :param candidate_count: int. The count of returned similar items
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """

    similar_items_list = get_similar_items(ItemSimilarity, **kwargs)

    return rank_similar_items_by_popularity_score(
        **kwargs, similar_items_list=similar_items_list
    )


def get_mktplace_related_queries_by_query(**kwargs):
    """
    Search the database to get fgm_related_queries_by_query given query_keyword with number of candidate count
    :param candidate_count: int
    :param query_keyword: str.
    :return: a recommendation list
    """
    candidate_count = kwargs["candidate_count"]
    query_keyword = kwargs["query_keyword"]

    try:
        related_queries_object = RelatedQueriesByQuery.objects(
            query=query_keyword
        ).get()
    except DoesNotExist:
        return []
    return related_queries_object.recommendations[:candidate_count]


def get_mktplace_related_queries_by_category(**kwargs):
    """
    Search the database to get related queries data by category path
    and get the result with number of candidate count
    :param category_path: str
    :param candidate_count: int
    :return: a recommendation list
    """
    category_path = kwargs["category_path"]
    candidate_count = kwargs["candidate_count"]
    try:
        related_queries_by_category_object = RelatedQueriesByCategory.objects(
            category_path=category_path
        ).get()
    except DoesNotExist:
        return []
    return related_queries_by_category_object.recommendations[:candidate_count]


def get_mktplace_related_categories_by_query(**kwargs):
    """
    Search the database to get related categories data by query
    and get the result with number of candidate count
    :param query_keyword: str
    :param candidate_count: int
    :return: a recommendation list
    """
    query_keyword = kwargs["query_keyword"]
    candidate_count = kwargs["candidate_count"]
    try:
        related_categories_by_query_object = RelatedCategoriesByQuery.objects(
            query=query_keyword
        ).get()
    except DoesNotExist:
        return []
    return related_categories_by_query_object.recommendations[:candidate_count]


def get_mktplace_picks_from_experts(**kwargs):
    """
    This function gets n categories and k recommendations for each category.
    if user exists, it fetches n categories from fgm_featured_first_layer_category_by_user
    If user does not exist, or does not return enough results,
    fetches n categories from fgm_popular_first_layer_category
    then uses these categories to get k recommendations from fgm_popular_item_by_category collections.

    :param user_id: int. If login, we will input a user_id else default 0
    :param category_count: int. No. of category items, default 5
    :param category_buffer: int. No. of buffer category items, default 5
    :param candidate_count: int. No. of recommended items, default 5
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: A list of category paths with their recommended items
    Example return value
    {
    "category1": ["item1", "item2", "item3"],
    "category2": ["item4", "item5", "item6"],
    "category3": ["item7", "item8", "item9"],
    }
    """
    return get_picks_from_experts(
        FeaturedFirstLayerCategoryByUser, PopularFirstLayerCategory, **kwargs
    )
