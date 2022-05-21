import json

from mongoengine import DoesNotExist
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
    ItemSimilarity,
)
from app.main.model.b2b_ent import ProjectUseThis, ProjectInspiration, PopularItem

# from app.main import bigquery_client
from flask import abort

from app.main.util.filter_deactivated_items import filter_deactivated_items
from app.main.util.general_service_functions import (
    filter_recently_view_streaming_based_on_time,
    search_people_also_buy,
    search_rerank,
    get_trending_now_all_category,
    get_similar_items,
    get_purchased_together_for_bundle,
)
from app.main.util.global_db_connection import glb_db_conn
from app.main.util.rec_api_redis_client import rec_api_redis_client


# from app.main.configuration.vault_vars_config import RECENTLY_VIEW_DB


def get_b2b_ent_purchased_together(**kwargs):
    """
    Search the database to get purchase together data by given item id
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
        purchase_bundle_object = PurchaseBundle.objects(item_id=item_id).get()
    except DoesNotExist:
        return []

    return filter_deactivated_items(
        recommendation_list=purchase_bundle_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def get_b2b_ent_similar_items(**kwargs):
    """
    Search the database to get similar item data by given target item
    :param item_id: str. Item ID
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


def get_b2b_ent_recommended_for_you(**kwargs):
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
        return get_b2b_ent_popular_item(candidate_count=candidate_count, **filter_args)
    return filter_deactivated_items(
        recommendation_list=recommend_for_you_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def get_b2b_ent_featured_category(**kwargs):
    """
    Search the database to get featured category data by user id
    and get the result with number of candidate count
    :param user_id: str
    :param candidate_count: int
    :return: a recommendation list
    """
    user_id = kwargs["user_id"]
    candidate_count = kwargs["candidate_count"]

    try:
        featured_category_object = FeaturedCategory.objects(user_id=user_id).get()
    except DoesNotExist as e:
        raise e
    return featured_category_object.recommendations[:candidate_count]


def get_b2b_ent_buy_it_again(**kwargs):
    """
    Search the database to get buy it again data by user id
    and get the result with number of candidate count
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
        buy_it_again_object = BuyItAgain.objects(user_id=user_id).get()
    except DoesNotExist:
        return []
    return filter_deactivated_items(
        recommendation_list=buy_it_again_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def get_b2b_ent_buy_it_again_mpg(**kwargs):
    """
    Search the database to get buy it again MPG data by user id
    and get the result with number of candidate count
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
        buy_it_again_mpg_object = BuyItAgainMPG.objects(user_id=user_id).get()
    except DoesNotExist:
        return []
    return filter_deactivated_items(
        recommendation_list=buy_it_again_mpg_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def get_b2b_ent_rec_for_you_search(**kwargs):
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
        return get_b2b_ent_popular_search_keyword(candidate_count=candidate_count)
    return rec_for_you_search_object.recommendations[:candidate_count]


def put_b2b_ent_user_defined_trending_now(**kwargs):
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


def get_b2b_ent_user_defined_trending_now(**kwargs):
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


def get_b2b_ent_trending_now_model(**kwargs):
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


def get_b2b_ent_trending_now(**kwargs):
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
    user_def_tn = get_b2b_ent_user_defined_trending_now(
        category_path=category_path,
        candidate_count=candidate_count,
        **filter_args,
    )
    tn_model = get_b2b_ent_trending_now_model(
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


def get_b2b_ent_trending_now_all_category(**kwargs):
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


def get_b2b_ent_people_also_buy(**kwargs):
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


def get_b2b_ent_seasonal_top_picks(**kwargs):
    """
    Search the database to get seasonal top picks data
    and get the result with number of candidate count
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
        seasonal_top_picks_object = SeasonalTopPicks.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e
    return filter_deactivated_items(
        recommendation_list=seasonal_top_picks_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


# def get_b2b_ent_recently_viewed(**kwargs):
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
#         f"WHERE event_name='page_view' AND app_id = 'b2b-web' AND user_id = '{user_id}' "
#         f"AND Date(collector_tstamp) BETWEEN DATE_SUB(current_date(), INTERVAL 7 DAY) AND current_date() "
#         f"AND unstruct_event_com_michaels_item_view_1_0_0.item_id NOT IN ("
#         f"SELECT DISTINCT unstruct_event_com_michaels_add_to_cart_1_0_0.item_id "
#         f"FROM `{RECENTLY_VIEW_DB}` "
#         f"WHERE user_id = '{user_id}' AND event_name = 'add_to_cart' AND app_id = 'b2b-web' "
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


def get_b2b_ent_project_use_this(**kwargs):
    """
    Search the database to get project use this data by given item id
    and get the result with number of candidate count
    :param item_id: str
    :param candidate_count: int
    Filter params to remove inactive projects
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    item_id = kwargs["item_id"]
    candidate_count = kwargs["candidate_count"]
    project_filter_args = {
        "table_name": kwargs["project_table_name"],
        "item_col_name": kwargs["project_item_col_name"],
        "check_col_name": kwargs["project_check_col_name"],
        "check_val": kwargs["project_check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        project_use_this_object = ProjectUseThis.objects(item_id=item_id).get()
    except DoesNotExist as e:
        raise e
    return filter_deactivated_items(
        recommendation_list=project_use_this_object.recommendations,
        return_number=candidate_count,
        **project_filter_args,
    )


def get_b2b_ent_project_inspiration(**kwargs):
    """
    Search the database to get project inspiration data by user id
    and get the result with number of candidate count
    :param user_id: str
    :param candidate_count: int
    :return: a recommendation list
    """
    user_id = kwargs["user_id"]
    candidate_count = kwargs["candidate_count"]

    try:
        project_inspiration_object = ProjectInspiration.objects(user_id=user_id).get()
    except DoesNotExist as e:
        raise e
    return project_inspiration_object.recommendations[:candidate_count]


def get_b2b_ent_popular_item(**kwargs):
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


def get_b2b_ent_recently_viewed_streaming(**kwargs):
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
    redis_hkey = "b2b_ent_streaming_recently_view"
    user_id = kwargs["user_id"]
    # get data from redis by given user_id
    data = rec_api_redis_client.hget(redis_hkey, user_id)
    # # raise 404 if user id not found
    if data is None:
        return []
    return filter_recently_view_streaming_based_on_time(data=data, **kwargs)


def get_b2b_ent_search_people_also_buy(**kwargs):
    """
    Provides recommendation services using item ids and scores for b2b ent search_people_also_buy
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


def post_b2b_ent_search_rerank(json_dict):
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


def get_b2b_ent_you_may_also_buy(**kwargs):
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
        return get_b2b_ent_popular_item(**kwargs)

    return filter_deactivated_items(
        recommendation_list=you_may_also_buy_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def get_b2b_ent_popular_search_keyword(**kwargs):
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


def get_b2b_ent_purchased_together_bundle(**kwargs):
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


def get_b2b_ent_streaming_trending_now_list(**kwargs):
    """
    Search redis b2b_ent_streaming_trending_now_list
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
