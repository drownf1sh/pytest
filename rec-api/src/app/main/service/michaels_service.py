import json

import pandas as pd
import time
import datetime

from app.main.database.cache import cache
from app.main.model.michaels import (
    BuyItAgain,
    BuyItAgainMPG,
    TrendingNowModel,
    UserDefTrendingNow,
    EventForYou,
    FeaturedCategory,
    PeopleAlsoBuy,
    PeopleAlsoView,
    PopularCategory,
    PopularEvent,
    PopularItem,
    PopularProject,
    ProjectInspiration,
    ProjectSimilarity,
    ProjectUseThis,
    PurchaseBundle,
    SeasonalTopPicks,
    SimilarEvents,
    RecForYouSearch,
    UserRecommend,
    PopularFirstLayerCategory,
    FeaturedFirstLayerCategoryByUser,
    PopularSearchKeyword,
    YouMayAlsoBuy,
    PopularItemByStore,
    PopularProductsInProjects,
    YesterdayPopularItem,
    NewProjects,
    UpcomingEvent,
    FavoriteItemForYou,
    TrendingEvent,
    PopularClearanceCategory,
    PopularClearanceItem,
    PopularSaleCategory,
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

from app.main.util.filter_archived_events import (
    filter_archived_events_in_mongo,
    filter_no_schedule_events_in_mongo,
)
from app.main.util.filter_deactivated_items import (
    filter_deactivated_items,
    filter_deactivated_items_in_time_range,
)
from app.main.util.general_service_functions import (
    filter_recently_view_streaming_based_on_time,
    search_people_also_buy,
    search_rerank,
    get_trending_now_all_category,
    get_similar_ad_items,
    get_similar_items,
    get_purchased_together_for_bundle,
    get_top_picks,
    get_shopping_cart_bundle,
    rank_similar_items_by_popularity_score,
    get_picks_from_experts,
    _fetch_popular_first_layer_category,
    get_image_url_by_categories,
)
from flask import abort
from mongoengine import DoesNotExist
from app.main.util.global_db_connection import glb_db_conn, redis_client, rec_db_conn

# from app.main.configuration.vault_vars_config import RECENTLY_VIEW_DB
from app.main.util.rec_api_redis_client import rec_api_redis_client

CACHE_TIMEOUT = 300


def get_michaels_recommended_for_you(**kwargs):
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
        return get_michaels_popular_item(candidate_count=candidate_count, **filter_args)
    return filter_deactivated_items(
        recommendation_list=recommend_for_you_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_similar_items", query_string=True
)
def get_michaels_similar_items(**kwargs):
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


def get_michaels_similar_ad_items(**kwargs):
    """
    Search the database to get similar item data by given target item
    :param item_id: str. Item ID
    :param candidate_count: int. The count of recommended non-ad items
    :param ad_candidate_count: int. The count of recommended ad items
    :param redis_similar_items_hash_key: str. The redis hash key for similar_items
    :param redis_similar_ad_items_hash_key: str. The redis hash key for similar_ad_items
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    similar_ad_items = get_similar_ad_items(**kwargs)
    if similar_ad_items:
        return similar_ad_items
    else:
        raise DoesNotExist


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="michaels_purchased_and_viewed_together",
    query_string=True,
)
def get_michaels_purchased_and_viewed_together(**kwargs):
    """
    Get both purchased_together and viewed_together results from database,
    Use view_weight to multiply view_score, the new score will be purchased_score + view_weight*viewed_score,
    rerank and return the results with number of candidate count
    :param item_id: str
    :param view_weight: double
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
    view_weight = kwargs["view_weight"]
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        purchased_together_object = PurchaseBundle.objects(item_id=item_id).get()
        try:
            viewed_together_object = ViewedTogether.objects(item_id=item_id).get()
            purchased_together_df = pd.DataFrame(
                list(
                    zip(
                        purchased_together_object.recommendations,
                        purchased_together_object.score,
                    )
                ),
                columns=["recommendations", "score"],
            )
            viewed_together_df = pd.DataFrame(
                list(
                    zip(
                        viewed_together_object.recommendations,
                        viewed_together_object.score,
                    )
                ),
                columns=["recommendations", "score"],
            )
            viewed_together_df["score"] = view_weight * viewed_together_df["score"]

            combined_together_df = purchased_together_df.merge(
                viewed_together_df, how="outer", on="recommendations"
            )
            combined_together_df["score"] = combined_together_df["score_x"].fillna(
                0
            ) + combined_together_df["score_y"].fillna(0)
            combined_together_df.sort_values(by="score", ascending=False, inplace=True)
            return filter_deactivated_items(
                recommendation_list=combined_together_df["recommendations"].tolist(),
                return_number=candidate_count,
                **filter_args,
            )
        except DoesNotExist:
            return filter_deactivated_items(
                recommendation_list=purchased_together_object.recommendations,
                return_number=candidate_count,
                **filter_args,
            )
    except DoesNotExist:
        try:
            viewed_together_object = ViewedTogether.objects(item_id=item_id).get()
            return filter_deactivated_items(
                recommendation_list=viewed_together_object.recommendations,
                return_number=candidate_count,
                **filter_args,
            )
        except DoesNotExist:
            return []


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_purchased_together", query_string=True
)
def get_michaels_purchased_together(**kwargs):
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


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_viewed_together", query_string=True
)
def get_michaels_viewed_together(**kwargs):
    """
    Search the database to get viewed together data by given item id
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
        viewed_together_object = ViewedTogether.objects(item_id=item_id).get()
    except DoesNotExist:
        return []
    return filter_deactivated_items(
        recommendation_list=viewed_together_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def put_michaels_user_defined_trending_now(**kwargs):
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


def get_michaels_user_defined_trending_now(**kwargs):
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


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_trending_now_model", query_string=True
)
def get_michaels_trending_now_model(**kwargs):
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
    timeout=CACHE_TIMEOUT, key_prefix="michaels_trending_now", query_string=True
)
def get_michaels_trending_now(**kwargs):
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
    user_def_tn = get_michaels_user_defined_trending_now(
        category_path=category_path,
        candidate_count=candidate_count,
        **filter_args,
    )
    tn_model = get_michaels_trending_now_model(
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


def get_michaels_trending_now_all_category(**kwargs):
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


def get_michaels_buy_it_again(**kwargs):
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


def get_michaels_buy_it_again_mpg(**kwargs):
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


def get_michaels_rec_for_you_search(**kwargs):
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
        return get_michaels_popular_search_keyword(candidate_count=candidate_count)
    return rec_for_you_search_object.recommendations[:candidate_count]


def get_michaels_featured_category(**kwargs):
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
    except DoesNotExist:
        return get_michaels_popular_category(candidate_count=candidate_count)
    return featured_category_object.recommendations[:candidate_count]


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_people_also_buy", query_string=True
)
def get_michaels_people_also_buy(**kwargs):
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


# Adding cached timeout of 300 secs for perf
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_people_also_view", query_string=True
)
def get_michaels_people_also_view(**kwargs):
    """
    Search the database to get people also view data by given item id
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
        people_also_view_object = PeopleAlsoView.objects(item_id=item_id).get()
    except DoesNotExist:
        return []
    return filter_deactivated_items(
        recommendation_list=people_also_view_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_seasonal_top_picks", query_string=True
)
def get_michaels_seasonal_top_picks(**kwargs):
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


# def get_michaels_recently_viewed(**kwargs):
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
#     return filter_deactivated_items(
#         recommendation_list=res,
#         return_number=candidate_count,
#         **filter_args,
#     )


def get_michaels_recently_viewed_streaming(**kwargs):
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
    redis_hkey = "mik_streaming_recently_view"
    user_id = kwargs["user_id"]

    # get data from redis by given user_id
    data = rec_api_redis_client.hget(redis_hkey, user_id)
    # # raise 404 if user id not found
    if data is None:
        return []
    return filter_recently_view_streaming_based_on_time(data=data, **kwargs)


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_project_use_this", query_string=True
)
def get_michaels_project_use_this(**kwargs):
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


def get_michaels_project_inspiration(**kwargs):
    """
    Search the database to get project inspiration data by user id
    and get the result with number of candidate count
    :param user_id: str
    :param candidate_count: int
    Filter params to remove inactive projects
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    user_id = kwargs["user_id"]
    candidate_count = kwargs["candidate_count"]
    project_filter_args = {
        "table_name": kwargs["project_table_name"],
        "item_col_name": kwargs["project_item_col_name"],
        "check_col_name": kwargs["project_check_col_name"],
        "check_val": kwargs["project_check_val"],
        "db_connection": glb_db_conn,
    }
    popular_project_filter_args = {
        "project_table_name": kwargs["project_table_name"],
        "project_item_col_name": kwargs["project_item_col_name"],
        "project_check_col_name": kwargs["project_check_col_name"],
        "project_check_val": kwargs["project_check_val"],
        "db_connection": glb_db_conn,
    }
    try:
        project_inspiration_object = ProjectInspiration.objects(user_id=user_id).get()
    except DoesNotExist:
        return get_michaels_popular_project(
            candidate_count=candidate_count, **popular_project_filter_args
        )
    return filter_deactivated_items(
        recommendation_list=project_inspiration_object.recommendations,
        return_number=candidate_count,
        **project_filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_popular_item", query_string=True
)
def get_michaels_popular_item(**kwargs):
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


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_similar_projects", query_string=True
)
def get_michaels_similar_projects(**kwargs):
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


def get_michaels_similar_items_for_bundle(**kwargs):
    """
    :param items_id_list: str. The bundle items ID list. Separated by space.
    :param candidate_count: int
    :param collection_name: str. DB collection for mik_similar_items
    :param redis_similar_items_hash_key: str. Redis key for mik_similar_items
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    items_id_list = kwargs["items_id_list"].strip().split(" ")
    candidate_count = kwargs["candidate_count"]
    collection_name = kwargs["collection_name"]
    redis_similar_items_hash_key = kwargs["redis_similar_items_hash_key"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }

    similar_items_list = rec_api_redis_client.hmget(
        redis_similar_items_hash_key, items_id_list
    )

    similar_items = []
    similar_items_score = []
    for item in similar_items_list:
        if item is not None:
            item_dict = json.loads(item)
            similar_items.extend(item_dict["recommendations"])
            similar_items_score.extend(item_dict["score"])

    if len(similar_items) == 0:
        similar_items_list = list(
            rec_db_conn.get_database_instance()[collection_name].find(
                {"item_id": {"$in": items_id_list}}, {"_id": 0}
            )
        )
        for item in similar_items_list:
            similar_items.extend(item["recommendations"])
            similar_items_score.extend(item["score"])

    if len(similar_items) == 0:
        raise DoesNotExist("Item ID not found")

    similar_items_df = pd.DataFrame(
        {"similar_items": similar_items, "similar_items_score": similar_items_score}
    )
    similar_items_df = similar_items_df.groupby(["similar_items"]).sum().reset_index()
    result = similar_items_df.sort_values(
        by=["similar_items_score", "similar_items"], ascending=[False, True]
    )["similar_items"].tolist()
    return filter_deactivated_items(
        recommendation_list=result,
        return_number=candidate_count,
        **filter_args,
    )


def get_michaels_event_for_you(**kwargs):
    """
    Search the database to get event for you data by given user id
    and return results with number of given candidate count
    :param user_id: str
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
    user_id = kwargs["user_id"]
    event_type = kwargs["event_type"]
    candidate_count = kwargs["candidate_count"]
    try:
        event_for_you_object = EventForYou.objects(user_id=user_id).get()
    except DoesNotExist:
        return get_michaels_popular_event(
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


def get_michaels_top_picks(**kwargs):
    """
    This service gets the top picks for the user in each category
    Then we fetch k recommendations for user_id from streaming_top_picks in Redis
    If that doesn't exist then get top k categories from mik_popular_first_layer_category in mongo
    then use these categories to get 1 recommendation from the mik_popular_item_by_category mongo collection

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
    timeout=CACHE_TIMEOUT, key_prefix="michaels_popular_event", query_string=True
)
def get_michaels_popular_event(**kwargs):
    """
    Search the database to get popular event data with number of candidate count
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


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_similar_events", query_string=True
)
def get_michaels_similar_events(**kwargs):
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


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_popular_category", query_string=True
)
def get_michaels_popular_category(**kwargs):
    """
    Search the database to get popular category data with number of candidate count
    :param candidate_count: int
    :return: a recommendation list
    """
    candidate_count = kwargs["candidate_count"]

    try:
        popular_category_object = PopularCategory.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e
    return popular_category_object.recommendations[:candidate_count]


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_popular_project", query_string=True
)
def get_michaels_popular_project(**kwargs):
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
    return filter_deactivated_items(
        recommendation_list=popular_project_object.recommendations,
        return_number=candidate_count,
        **project_filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_trending_project", query_string=True
)
def get_michaels_trending_project(**kwargs):
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


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="michaels_popular_search_keyword",
    query_string=True,
)
def get_michaels_popular_search_keyword(**kwargs):
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


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="michaels_search_people_also_buy",
    query_string=True,
)
def get_michaels_search_people_also_buy(**kwargs):
    """
    Provides recommendation services using item ids and scores for michaels search_people_also_buy
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


def post_michaels_search_rerank(json_dict):
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


def get_michaels_picks_from_experts(**kwargs):
    """
    This function gets n categories and k recommendations for each category.
    if user exists, it fetches n categories from mik_featured_first_layer_category_by_user
    If user does not exist, or does not return enough results,
    fetches n categories from mik_popular_first_layer_category
    then uses these categories to get k recommendations from mik_popular_item_by_category collections.

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


def get_michaels_you_may_also_buy(**kwargs):
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
        return get_michaels_popular_item(**kwargs)
    return filter_deactivated_items(
        recommendation_list=you_may_also_buy_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def get_michaels_favorite_item_for_you(**kwargs):
    """
    Fetches the favorite item for you recommendations for a user id
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
        favorite_item_for_you_object = FavoriteItemForYou.objects(user_id=user_id).get()
    except DoesNotExist:
        favorite_item_for_you_object = FavoriteItem.objects(group_id=0).get()

    return filter_deactivated_items(
        recommendation_list=favorite_item_for_you_object.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


def get_michaels_popular_item_by_store(**kwargs):
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


def get_michaels_purchased_together_bundle(**kwargs):
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


def get_michaels_popular_item_by_category(**kwargs):
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


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="michaels_popular_products_in_projects",
    query_string=True,
)
def get_michaels_popular_products_in_projects(**kwargs):
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
    key_prefix="michaels_yesterday_popular_item",
    query_string=True,
)
def get_michaels_yesterday_popular_item(**kwargs):
    """
    Search the database to get mik yesterday popular item data with number of candidate count
    :param candidate_count: int
    :return: a recommendation list of mik_yesterday_popular_item
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
    timeout=CACHE_TIMEOUT, key_prefix="michaels_new_projects", query_string=True
)
def get_michaels_new_projects(**kwargs):
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


# Adding cached timeout of 300 secs for perf. testing
@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_upcoming_event", query_string=True
)
def get_michaels_upcoming_event(**kwargs):
    """
    Search the database to get upcoming events id and schedules id with number of candidate count
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
    :return: a dict with event id list and schedules id list
    """
    candidate_count = kwargs["candidate_count"]
    event_type = kwargs["event_type"]
    query_timestamp = int(time.time()) % (24 * 3600) // 900 * 900
    # db_name = kwargs["filter_archived_events_args"]["db_name"]
    # table_name = kwargs["filter_archived_events_args"]["table_name"]
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
    timeout=CACHE_TIMEOUT, key_prefix="michaels_trending_event", query_string=True
)
def get_michaels_trending_event(**kwargs):
    """
    Search the database to get mik trending event data with number of candidate count
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
    key_prefix="michaels_popular_clearance_category",
    query_string=True,
)
def get_michaels_popular_clearance_category(**kwargs):
    """
    This service gets the popular clearance category with number of candidate count.
    :param candidate_count: int
    :return a recommendation list
    """
    candidate_count = kwargs["candidate_count"]

    try:
        popular_clearance_category = PopularClearanceCategory.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e

    return popular_clearance_category.recommendations[:candidate_count]


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="michaels_popular_clearance_item",
    query_string=True,
)
def get_michaels_popular_clearance_item(**kwargs):
    """
    If user_id is present, then search redis mik_streaming_top_clearance
    Otherwise, search MongoDB mik_popular_clearance_item collection to get recommendations
    with number of candidate count
    :param user_id: str
    :param candidate_count: int
    :return: a recommendation list

    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :param badges_name: str. The badges object name of a product
    :param badges_check_name: str. Based on specific column to check badges val
    :param badges_check_val: bool. The value to be checked
    :param badges_start_date_name: str. The col name to query start time
    :param badges_expiration_date_name: str. The col name to query end time
    """
    user_id = kwargs["user_id"]
    candidate_count = kwargs["candidate_count"]
    redis_popular_clearance_item_hash_key = kwargs[
        "redis_popular_clearance_item_hash_key"
    ]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    current_time = datetime.datetime.utcnow()
    filter_badges_args = {
        "badges_name": kwargs["badges_name"],
        "badges_check_name": kwargs["badges_check_name"],
        "badges_check_val": kwargs["badges_check_val"],
        "current_time": current_time,
        "badges_start_date_name": kwargs["badges_start_date_name"],
        "badges_expiration_date_name": kwargs["badges_expiration_date_name"],
    }
    # get data from redis by user_id if user_id is present
    if user_id:
        redis_popular_clearance_item = rec_api_redis_client.hget(
            redis_popular_clearance_item_hash_key, user_id
        )
        if redis_popular_clearance_item:
            popular_clearance_items = json.loads(redis_popular_clearance_item)[
                "recommendations"
            ]
            return filter_deactivated_items_in_time_range(
                recommendation_list=popular_clearance_items,
                return_number=candidate_count,
                **filter_args,
                **filter_badges_args,
            )
    try:
        popular_clearance_item_object = PopularClearanceItem.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e
    return filter_deactivated_items_in_time_range(
        recommendation_list=popular_clearance_item_object.recommendations,
        return_number=candidate_count,
        **filter_args,
        **filter_badges_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="michaels_popular_sale_category",
    query_string=True,
)
def get_michaels_popular_sale_category(**kwargs):
    """
    This service gets the popular sale category with number of candidate count.
    :param candidate_count: int
    :return a recommendation list
    """
    candidate_count = kwargs["candidate_count"]

    try:
        popular_sale_category = PopularSaleCategory.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e

    return popular_sale_category.recommendations[:candidate_count]


@cache.cached(
    timeout=CACHE_TIMEOUT, key_prefix="michaels_popular_sale_item", query_string=True
)
def get_michaels_popular_sale_item(**kwargs):
    """
    If user_id is present, then search redis mik_streaming_top_sale
    Otherwise, search MongoDB mik_popular_sale_item collection to get recommendations
    with number of candidate count
    :param user_id: str
    :param candidate_count: int
    :return: a recommendation list

    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering

    """
    user_id = kwargs["user_id"]
    candidate_count = kwargs["candidate_count"]
    redis_popular_sale_item_hash_key = kwargs["redis_popular_sale_item_hash_key"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    current_time = datetime.datetime.utcnow()
    filter_badges_args = {
        "badges_name": kwargs["badges_name"],
        "badges_check_name": kwargs["badges_check_name"],
        "badges_check_val": kwargs["badges_check_val"],
        "current_time": current_time,
        "badges_start_date_name": kwargs["badges_start_date_name"],
        "badges_expiration_date_name": kwargs["badges_expiration_date_name"],
    }
    if user_id:
        redis_popular_sale_item = rec_api_redis_client.hget(
            redis_popular_sale_item_hash_key, user_id
        )
        if redis_popular_sale_item:
            popular_sale_item_list = json.loads(redis_popular_sale_item)[
                "recommendations"
            ]
            return filter_deactivated_items_in_time_range(
                recommendation_list=popular_sale_item_list,
                return_number=candidate_count,
                **filter_args,
                **filter_badges_args,
            )
    try:
        popular_sale_item_object = PopularSaleItem.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e
    return filter_deactivated_items_in_time_range(
        recommendation_list=popular_sale_item_object.recommendations,
        return_number=candidate_count,
        **filter_args,
        **filter_badges_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="michaels_popular_visited_events",
    query_string=True,
)
def get_michaels_popular_visited_events(**kwargs):
    """
    This service gets the popular visited events with number of candidate count.
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


def get_michaels_streaming_trending_now_list(**kwargs):
    """
    Search redis mik_streaming_trending_now_list
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
    key_prefix="michaels_popular_first_layer_category",
    query_string=True,
)
def get_michaels_popular_first_layer_category(**kwargs):
    """
    Search the database to get mik popular_first_layer_category data with number of candidate count
    :param candidate_count: int
    :return a recommendation list
    """
    candidate_count = kwargs["candidate_count"]

    return _fetch_popular_first_layer_category(
        PopularFirstLayerCategory, candidate_count
    )


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="michaels_popular_visited_projects",
    query_string=True,
)
def get_michaels_popular_visited_projects(**kwargs):
    """
    Search the database to get mik popular_visited_projects data with number of candidate count
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
    key_prefix="michaels_popular_visited_items",
    query_string=True,
)
def get_michaels_popular_visited_items(**kwargs):
    """
    Search the database to get mik popular_visited_items data with number of candidate count
    :param candidate_count: int
    :return a recommendation list
    """
    candidate_count = kwargs["candidate_count"]

    try:
        popular_visited_items = PopularVisitedItems.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e

    return popular_visited_items.recommendations[:candidate_count]


def get_michaels_shopping_cart_bundle(**kwargs):
    """
    Search redis and database to get mik shopping cart bundle data with number of candidate count
    :param items_id_list: str. The bundle items ID list. Separated by space.
    :param candidate_count: int
    :param redis_similar_items_hash_key: str. Redis key for mik_similar_items
    :param collection_name: str. mik_purchased_together
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    return get_shopping_cart_bundle(**kwargs)


def get_michaels_similar_items_in_same_store(**kwargs):
    """
    Search the database to get ea_same_store_similar_items by given item id
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
        similar_items_in_same_store = SimilarItemsInSameStore.objects(
            item_id=item_id
        ).get()
    except DoesNotExist:
        return []
    return filter_deactivated_items(
        recommendation_list=similar_items_in_same_store.recommendations,
        return_number=candidate_count,
        **filter_args,
    )


@cache.cached(
    timeout=CACHE_TIMEOUT,
    key_prefix="michaels_popular_products_in_events",
    query_string=True,
)
def get_michaels_popular_products_in_events(**kwargs):
    """
    Search the database to get mik_popular_products_in_events data with number of candidate count
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


def get_michaels_related_categories_by_category(**kwargs):
    """
    Search the database to get related categories data by category path
    and get the result with number of candidate count
    :param category_path: str
    :param candidate_count: int
    :return: a dict with category image pairs
    """
    category_path = kwargs["category_path"]
    try:
        related_categories_by_category_object = RelatedCategoriesByCategory.objects(
            category_path=category_path
        ).get()
    except DoesNotExist:
        return []

    result = get_image_url_by_categories(
        related_categories_by_category_object.recommendations, **kwargs
    )
    return result


def get_michaels_similar_items_by_popularity(**kwargs):
    """
    Search the database to get a list of similar items given target item Id
    then order the results based on popularity score in mik_popular_master_items database collection
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


def get_michaels_related_queries_by_query(**kwargs):
    """
    Search the database to get mik_related_queries_by_query given query_keyword with number of candidate count
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


def get_michaels_related_queries_by_category(**kwargs):
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


def get_michaels_related_categories_by_query(**kwargs):
    """
    Search the database to get related categories data by query
    and get the result with number of candidate count
    :param query_keyword: str
    :param candidate_count: int
    :return: a dict with category image pairs
    """
    query_keyword = kwargs["query_keyword"]

    try:
        related_categories_by_query_object = RelatedCategoriesByQuery.objects(
            query=query_keyword
        ).get()
    except DoesNotExist:
        return []

    result = get_image_url_by_categories(
        related_categories_by_query_object.recommendations, **kwargs
    )
    return result
