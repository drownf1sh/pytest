"""
This module is used for general usages in service functions
"""
import datetime
import json
from collections import OrderedDict

import numpy as np
import pandas as pd
import pickle
import time
from mongoengine import DoesNotExist
from app.main import rec_db_conn, glb_db_conn
from app.main.recommender.ml_models._similarity import similarity
from app.main.util.exception_handler import NotEnoughRecommendations
from app.main.util.filter_deactivated_items import (
    filter_deactivated_items,
    filter_deactivated_items_df,
)
from app.main.util.global_db_connection import sch_db_conn
from app.main.util.global_vars import (
    ad_items_status_redis_hkey,
    gcp_publisher,
    snowflake_id_generator,
)
from app.main.configuration.vault_vars_config import PUBSUB_TOPIC
from app.main.util.rec_api_redis_client import rec_api_redis_client


def filter_recently_view_streaming_based_on_time(data: str, **kwargs):
    """
    This function is used for all recently viewed streaming services
    :param data: str
    :param date_interval: int
    :param candidate_count: int
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: result_list: list
    """
    date_interval = kwargs["date_interval"]
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    # get view list and view time list from json data
    view_list = json.loads(data)["view_list"]
    view_time = json.loads(data)["view_time"]
    # check corner cases
    if len(view_list) != len(view_time):
        raise ValueError("The length of view list and view time list should be equal")
    res_list = []
    # iterate over the two lists and filter items by the time interval
    for i in range(len(view_list)):
        # The string time format may changed in future
        delta_time = datetime.datetime.now() - datetime.datetime.strptime(
            view_time[i][:-5], "%Y-%m-%dT%H:%M:%S"
        )
        if delta_time.days <= date_interval:
            res_list.append(view_list[i])

    return filter_deactivated_items(
        recommendation_list=res_list,
        return_number=candidate_count,
        **filter_args,
    )


def search_people_also_buy(**kwargs):
    """
    This function is used for all search_people_also_buy recommendation services using item ids and scores
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
    items_ids = kwargs["items_id_list"]
    candidate_count = kwargs["candidate_count"]
    collection_name = kwargs["collection_name"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    items_id_list = items_ids.strip().split(" ")

    if "items_scores" in kwargs and kwargs["items_scores"] is not None:
        items_scores_list = list(map(float, kwargs["items_scores"].strip().split(" ")))
    else:
        items_scores_list = [1.0] * len(items_id_list)

    if len(items_id_list) != len(items_scores_list):
        raise ValueError("Length of items ids list and items scores list must match")

    # Create dataframe to map item_id to weight
    item_weight_df = pd.DataFrame(
        np.column_stack([items_id_list, items_scores_list]),
        columns=["item_id", "weight"],
    )

    # Fetch document of recommendations list from mongo
    recommended_items_list = list(
        rec_db_conn.get_database_instance()[collection_name].find(
            {"item_id": {"$in": items_id_list}}, {"_id": 0}
        )
    )
    if len(recommended_items_list) == 0:
        raise DoesNotExist
    else:
        # Create dataframe from mongo doc
        rec_df = pd.DataFrame(recommended_items_list)
        # Merging recommedations df with weights df
        rec_df = pd.merge(rec_df, item_weight_df, on="item_id")
        # exploding scores and recommendations to columns from lists
        rec_df = (
            rec_df.set_index(["item_id", "weight"])
            .apply(pd.Series.explode)
            .reset_index()
        )
        # Assigning numeric values to weight column
        rec_df["weight"] = pd.to_numeric(rec_df["weight"])
        # Multiplying weights with scores
        rec_df["weighted_score"] = rec_df["weight"].values * rec_df["score"].values
        # Removing unwanted columns
        rec_df = rec_df.drop(["item_id", "weight", "score"], axis=1)
        # Grouping by recommendations and summing up based on weighted score
        rec_df = rec_df.groupby("recommendations")["weighted_score"].sum().reset_index()
        # Removing the elements that are part of the original items id list
        rec_df = rec_df[~rec_df["recommendations"].isin(items_id_list)].reset_index(
            drop=True
        )
        # Sorting based on weighted scores in descending order, if same score, order by sku number in ascending order
        rec_df = rec_df.sort_values(
            by=["weighted_score", "recommendations"], ascending=(False, True)
        ).reset_index(drop=True)
        # Storing final recommendations as a list
        result = rec_df["recommendations"].tolist()
        return filter_deactivated_items(
            recommendation_list=result, return_number=candidate_count, **filter_args
        )


def get_item_vector_df_redis(redis_hash_key: str, items_ids_list: list):
    """
    Used to fetch the item vector of item ids from redis
    :param redis_hash_key: str. The redis hash key used to store item vector of item ids
    :param items_ids_list: list. The list of item ids to access their vectors

    :return: Data frame of the resulting item vector as value for given item ids
    """
    raw_item_vectors_list = rec_api_redis_client.hmget(redis_hash_key, items_ids_list)
    df = pd.DataFrame({"sku_number": items_ids_list, "vectors": raw_item_vectors_list})
    df["vectors"] = df["vectors"].apply(
        lambda x: pickle.loads(x) if x is not None else []
    )
    df = df[df["vectors"].map(lambda d: len(d)) > 0]
    df.dropna(inplace=True)
    df.reset_index(inplace=True, drop=True)
    df2 = pd.DataFrame(df["vectors"].to_list())
    df = pd.concat([df, df2], axis=1)
    return df


def search_rerank(
    items_ids: str,
    order_history: str,
    redis_hash_key: str,
    order_history_weights: str,
):
    """
    Reranks the search with the weighted sum of similarity score between order history and search history
    :param items_ids: str. The list of item IDs of search results. Separated by space.
    :param order_history: str. The list of item IDs of order history. Separated by space
    :param redis_hash_key: str. The redis hash key used to store item vector of item ids
    :param order_history_weights: str. The list of order history weights. Separated by space, default to all 1s.

    :return: List of reranked search results with score
    """
    items_ids_list = items_ids.strip().split(" ")
    order_history_list = order_history.strip().split(" ")
    if order_history_weights:
        order_history_weights_list = list(
            map(float, order_history_weights.strip().split(" "))
        )
    else:
        order_history_weights_list = [1 for _ in range(len(order_history_list))]

    if len(order_history_list) != len(order_history_weights_list):
        raise ValueError(
            "Length of order history list and items weights list must match"
        )

    # Combine duplicate order_history items
    order_history_df = pd.DataFrame(
        {
            "order_history_item": order_history_list,
            "order_history_score": order_history_weights_list,
        }
    )
    order_history_df = (
        order_history_df.groupby("order_history_item").sum().reset_index()
    )
    order_history_list = order_history_df["order_history_item"].to_list()
    order_history_weights_list = order_history_df["order_history_score"].to_list()

    # Get item id vectors df
    item_id_vectors_df = get_item_vector_df_redis(redis_hash_key, items_ids_list)
    # Get order item id vectors df
    order_id_vectors_df = get_item_vector_df_redis(redis_hash_key, order_history_list)
    if item_id_vectors_df.empty:
        raise DoesNotExist("Item ID not found")
    elif order_id_vectors_df.empty:
        return dict.fromkeys(items_ids_list, 1)

    # Creating a order history weights data frame to map order history item with weights
    order_hist_weights_df = pd.DataFrame(
        zip(order_history_list, order_history_weights_list),
        columns=["sku_number", "weights"],
    )

    # Merging to combine the weights only for the sku numbers that exist in the collection
    weights_df = pd.merge(
        order_hist_weights_df, order_id_vectors_df, how="inner", on=["sku_number"]
    )
    weights_df = weights_df[["weights"]].T

    # Calculating the similarity data frame and putting it in a dataframe
    sim_df = similarity(item_id_vectors_df.iloc[:, 2:], order_id_vectors_df.iloc[:, 2:])

    # Calculating a weighted similarity by multiplying it by weights and similarity
    weighted_sim_df = sim_df.mul(weights_df.values)

    # Calculating the weighted average similarity for all the item_ids
    weighted_avg_df = weighted_sim_df.sum(axis=1) / weights_df.sum(axis=1).iloc[0]

    # Concatenating item ids to calculated weighted similarity
    res_df = pd.concat([item_id_vectors_df.iloc[:, 0], weighted_avg_df], axis=1)
    res_df.columns = ["sku_num", "weighted_avg"]

    # Sorting based on the weighted similarity score
    items_ids_df = pd.DataFrame(items_ids_list, columns=["sku_num"])
    res_df = items_ids_df.merge(res_df, how="left", on="sku_num").fillna(-1)
    res_df = res_df.sort_values(by=["weighted_avg", "sku_num"], ascending=[False, True])
    result = res_df.set_index("sku_num").to_dict()["weighted_avg"]
    return result


def get_trending_now_all_category(**kwargs):
    """
    Retrieves the dict of category path and recommendations from MongoDB for user defined trending now and trending now models
    :param user_defined_trending_now: The MongoDB Collection for user defined trending now model
    :param trending_now: The MongoDB Collection for trending now model
    :param candidate_count: The count of recommendations that need to returned for each category path
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: List of dict of category path and recommendations
    """
    candidate_count = kwargs["candidate_count"]
    trending_now = kwargs["trending_now"]
    user_defined_trending_now = kwargs["user_defined_trending_now"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    # get user defined trending now categories & items
    user_defined_trending_now_df = pd.DataFrame(
        list(
            rec_db_conn.get_database_instance()[user_defined_trending_now].find(
                {"recommendations": {"$ne": []}}
            )
        ),
        columns=["category_path", "recommendations"],
    )

    # Filter out inactive items
    user_defined_trending_now_df = filter_deactivated_items_df(
        recommendation_df=user_defined_trending_now_df,
        rec_col="recommendations",
        return_number=candidate_count,
        **filter_args,
    )

    # get trending now model categories & items
    trending_now_model_df = pd.DataFrame(
        list(
            rec_db_conn.get_database_instance()[trending_now].find(
                {"recommendations": {"$ne": []}}
            )
        ),
        columns=["category_path", "recommendations"],
    )
    trending_now_model_df.rename(
        columns={"recommendations": "model_recommendations"}, inplace=True
    )
    # Filter out inactive items
    trending_now_model_df = filter_deactivated_items_df(
        recommendation_df=trending_now_model_df,
        rec_col="model_recommendations",
        return_number=candidate_count,
        **filter_args,
    )
    # merge two dataframe together
    combined_trending_now_df = user_defined_trending_now_df.merge(
        trending_now_model_df, how="outer", on="category_path"
    )
    # if user defined trending now doesn't exist, use trending now model's data for
    # these categories
    combined_trending_now_df["recommendations"] = combined_trending_now_df[
        "recommendations"
    ].mask(
        (
            (~combined_trending_now_df["recommendations"].astype(bool))
            | (combined_trending_now_df["recommendations"].isna())
        )
        & ~combined_trending_now_df["model_recommendations"].isna(),
        combined_trending_now_df["model_recommendations"],
    )

    # drop model_recommendations column
    combined_trending_now_df = combined_trending_now_df.drop(
        "model_recommendations", axis=1
    )

    # remove columns with empty recommmendations list
    combined_trending_now_df = combined_trending_now_df[
        combined_trending_now_df["recommendations"].astype(bool)
    ]
    return combined_trending_now_df.to_dict(orient="records")


def get_similar_items(similar_items_model, **kwargs):
    """
    :param item_id: str. Item ID
    :param candidate_count: int. default = 5. The count of non-ad similar items
    # :param ad_candidate_count: int. default = 5. The count of ad similar items
    :param redis_similar_items_hash_key: str. The redis hash key for similar items
    :param similar_items_model: object. Model object for similar items
    # :param redis_similar_ad_items_hash_key: str. The redis hash key for similar ad items
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: similar items recommendation list
    """
    item_id = kwargs["item_id"]
    candidate_count = kwargs["candidate_count"]
    # ad_candidate_count = kwargs["ad_candidate_count"]
    redis_similar_items_hash_key = kwargs["redis_similar_items_hash_key"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    # similar_ad_items = get_similar_ad_items(**kwargs)
    #
    # # If the amount of ad similar items is less than ad_candidate_count, recommend
    # # more non-ad items
    # similar_items = redis_client.hget(redis_similar_items_hash_key, item_id)
    # if similar_items:
    #     similar_items = pickle.loads(similar_items)["recommendations"]
    #     final_candidate_count = candidate_count + ad_candidate_count
    #     # Filter inactive items from similar_items list
    #     filtered_sim_items = filter_deactivated_items(
    #         recommendation_list=similar_items,
    #         return_number=final_candidate_count,
    #         **filter_args,
    #     )
    #     # Combine ad similar items and no-ad similar items. Exclude ad items from
    #     # non-ad items list
    #     for similar_item in filtered_sim_items:
    #         if (
    #             similar_item not in similar_ad_items
    #             and len(similar_ad_items) < final_candidate_count
    #         ):
    #             similar_ad_items.append(similar_item)
    # return similar_ad_items

    # Return non-add items with number of candidate count
    similar_items = rec_api_redis_client.hget(redis_similar_items_hash_key, item_id)
    if similar_items:
        similar_items = json.loads(similar_items)["recommendations"]
    else:
        try:
            similar_items = (
                similar_items_model.objects(item_id=item_id).get().recommendations
            )
        except DoesNotExist:
            return []

    return filter_deactivated_items(
        recommendation_list=similar_items,
        return_number=candidate_count,
        **filter_args,
    )


def get_similar_ad_items(**kwargs):
    """
    :param item_id: str. Item ID
    :param ad_candidate_count: int. default = 5. The count of ad similar items
    :param redis_similar_ad_items_hash_key: str. The redis hash key for similar ad items
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: similar ad items recommendation list
    """
    item_id = kwargs["item_id"]
    ad_candidate_count = kwargs["ad_candidate_count"]
    redis_similar_ad_items_hash_key = kwargs["redis_similar_ad_items_hash_key"]
    similar_items_api = kwargs["similar_items_api"]

    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    # Use redis hash get similar ad items
    similar_ad_items = rec_api_redis_client.hget(
        redis_similar_ad_items_hash_key, item_id
    )

    if similar_ad_items:
        similar_ad_items = json.loads(similar_ad_items)["recommendations"]
        filtered_sim_ad_items = filter_deactivated_items(
            recommendation_list=similar_ad_items,
            return_number=len(similar_ad_items),
            **filter_args,
        )
        if filtered_sim_ad_items:
            similar_ad_items_status = rec_api_redis_client.hmget(
                ad_items_status_redis_hkey, filtered_sim_ad_items
            )
            active_similar_ad_items = []
            k = 0
            while len(active_similar_ad_items) < ad_candidate_count and k < len(
                similar_ad_items_status
            ):
                if (
                    similar_ad_items_status[k]
                    and json.loads(similar_ad_items_status[k]) == 1
                ):
                    active_similar_ad_items.append(filtered_sim_ad_items[k])
                k += 1
        else:
            return []

        # push ads items info to gcp pubsub
        pubsub_message = push_similar_ad_items_pubsub(
            item_id=item_id, ad_items_id=active_similar_ad_items
        )
        if similar_items_api:
            return active_similar_ad_items
        else:
            return pubsub_message["products"]
    else:
        return []


def push_similar_ad_items_pubsub(
    item_id: str,
    ad_items_id: list,
):
    products_list = []
    for ad_item_id in ad_items_id:
        products_list.append(
            {
                "skuNumber": str(ad_item_id),
                "weight": 100,
                "adsId": "REC-" + str(next(snowflake_id_generator)),
            }
        )

    pubsub_message = {
        "targetingSku": [item_id],
        "timeMillis": round(time.time() * 1000),
        "products": products_list,
    }
    gcp_publisher.publish(PUBSUB_TOPIC, json.dumps(pubsub_message).encode("utf-8"))
    return pubsub_message


def get_purchased_together_for_bundle(items_ids_list: list, collection_name: str):
    """
    Get recommendations list from purchased together collection by sum score
    :param items_ids_list: list. The list of item ids to access their vectors
    :param collection_name: list. The collection used to access items IDs
    :return: a recommendation list
    """
    purchased_together_items_list = list(
        rec_db_conn.get_database_instance()[collection_name].find(
            {"item_id": {"$in": items_ids_list}}, {"_id": 0}
        )
    )
    if len(purchased_together_items_list) == 0:
        return []
    else:
        items_recommendation_df = pd.DataFrame(purchased_together_items_list)
        items_recommendation_df = items_recommendation_df.apply(pd.Series.explode)
        items_recommendation_df.dropna(inplace=True)
        items_recommendation_df = (
            items_recommendation_df.groupby(["recommendations"]).sum().reset_index()
        )
        result = items_recommendation_df.sort_values(
            by=["score", "recommendations"], ascending=[False, True]
        )["recommendations"].tolist()
        return result


def get_top_picks(popular_first_layer_category, **kwargs):
    """
    This service gets the top picks for the user in each category
    Then we fetch k recommendations for user_id from streaming_top_picks in Redis
    If that doesn't exist then get top k categories from popular_first_layer_category in mongo
    then use these categories to get 1 recommendation from the popular_item_by_category mongo collection

    :param popular_first_layer_category: The PopularFirstLayerCategory collection object
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
    user_id = kwargs["user_id"]
    candidate_count = kwargs["candidate_count"]
    redis_hash_key = kwargs["redis_hash_key"]
    collection_name = kwargs["collection_name"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    # Adding a buffer to get additional categories from the collections
    # So that after filtering we can atleast get the original count
    category_buffer = 5
    data = rec_api_redis_client.hget(redis_hash_key, user_id)
    if data:
        rec_items = json.loads(data)["recommendations"]
        return filter_deactivated_items(
            recommendation_list=rec_items, return_number=candidate_count, **filter_args
        )

    try:
        popular_first_layer_category_object = popular_first_layer_category.objects(
            group_id=0
        ).get()
        category_list = popular_first_layer_category_object.recommendations[
            : (candidate_count + category_buffer)
        ]
        rec_df = general_picks_function(
            category_list=category_list,
            return_number=1,
            collection_name=collection_name,
            **filter_args,
        )
        result = rec_df.explode("recommendations")["recommendations"].tolist()[
            :candidate_count
        ]
        if len(result) < candidate_count:
            raise NotEnoughRecommendations
        return result
    except DoesNotExist as e:
        raise e


def general_picks_function(category_list, return_number, collection_name, **kwargs):
    """
    This is a common function to get filtered recommendations for a given
    category list from mongodb collection specified
    :param category_list: list,
    :param return_number: int,
    :param collection_name: str,
    :return: a dataframe consisting of category_paths and recommendations

    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering

    """
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }

    collection = rec_db_conn.get_database_instance()[collection_name]
    rec_df = pd.DataFrame(
        list(collection.find({"category_path": {"$in": category_list}}, {"_id": 0}))
    )
    # if empty dataframe
    if rec_df.empty or rec_df.dropna().empty:
        raise NotEnoughRecommendations
    # Create an index for sorting based on the category list order
    sorterIndex = dict(zip(category_list, range(len(category_list))))
    # Generate a rank column based on the index for sorting
    rec_df["rec_rank"] = rec_df["category_path"].map(sorterIndex)
    # sort by the same order as the rec_rank column
    rec_df.sort_values(by=["rec_rank"], inplace=True)
    # Apply inactive items filter to recommendation_df
    filter_deactivated_items_df(
        recommendation_df=rec_df,
        return_number=return_number,
        rec_col="recommendations",
        **filter_args,
    )
    # remove category rows with recommendations less than return_number
    rec_df = rec_df[rec_df["recommendations"].apply(len).ge(return_number)]
    return rec_df


def get_similar_items_for_bundle(
    items_id_list: list, redis_similar_items_hash_key: str, collection_name: str
):
    """
    Search redis to get similar items for bundle. Only used for shopping_cart_bundle service.
    :param items_id_list: str. The bundle items ID list.
    :param redis_similar_items_hash_key: str. Redis key for mik_similar_items or fgm_similar_items
    :param collection_name: str. collection_name for similar_items
    :return: a recommendation list
    """
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
        return []

    similar_items_df = pd.DataFrame(
        {"similar_items": similar_items, "similar_items_score": similar_items_score}
    )
    similar_items_df = similar_items_df.groupby(["similar_items"]).sum().reset_index()
    sorted_similar_item_list = similar_items_df.sort_values(
        by=["similar_items_score", "similar_items"], ascending=[False, True]
    )["similar_items"].tolist()

    return sorted_similar_item_list


def get_shopping_cart_bundle(**kwargs):
    """
    Search redis and database to get fgm shopping cart bundle data with number of candidate count
    :param items_id_list: str. The bundle items ID list. Separated by space.
    :param candidate_count: int
    :param redis_similar_items_hash_key: str. Redis key for mik_similar_items || fgm_similar_items
    :param collection_name: str. mik_purchased_together || fgm_purchased_together
    Filter params to remove inactive items
    :param table_name: str. The name of target table to be searched
    :param item_col_name: str. Based on specific column to search
    :param check_col_name: str. Based on specific column to check val
    :param check_val: str. The value to be checked
    :param db_connection: Given db connection to do filtering
    :return: a recommendation list
    """
    items_ids_list = kwargs["items_id_list"].strip().split(" ")
    redis_similar_items_hash_key = kwargs["redis_similar_items_hash_key"]
    purchased_together_collection_name = kwargs["purchased_together_collection_name"]
    similar_items_collection_name = kwargs["similar_items_collection_name"]
    candidate_count = kwargs["candidate_count"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    purchased_together_for_bundle_list = get_purchased_together_for_bundle(
        items_ids_list, purchased_together_collection_name
    )

    purchased_together_for_bundle_list = filter_deactivated_items(
        recommendation_list=purchased_together_for_bundle_list,
        return_number=candidate_count,
        **filter_args,
    )

    if len(purchased_together_for_bundle_list) == candidate_count:
        return purchased_together_for_bundle_list
    else:
        supplement_count = candidate_count - len(purchased_together_for_bundle_list)
        similar_items_for_bundle_list = get_similar_items_for_bundle(
            items_ids_list, redis_similar_items_hash_key, similar_items_collection_name
        )

        # remove duplications
        similar_items_for_bundle_list = [
            item
            for item in similar_items_for_bundle_list
            if item not in purchased_together_for_bundle_list
        ]

        similar_items_for_bundle_list = filter_deactivated_items(
            recommendation_list=similar_items_for_bundle_list,
            return_number=supplement_count,
            **filter_args,
        )

        return purchased_together_for_bundle_list + similar_items_for_bundle_list


def rank_similar_items_by_popularity_score(**kwargs):
    """
    This function is used to reorder similar_items list based on the popularity score in popular_master_items,
    if similar_item is not found, popular_score would be 0.
    The order would be score(descending), and item_id(ascending)
    :param similar_items_list: list. A list of similar_item returned by get_similar_items
    :param collection_name: str. The mongodb collection to access popularity score
    :return: a recommendation list
    """
    collection_name = kwargs["collection_name"]
    similar_items_list = kwargs["similar_items_list"]

    # Return empty list if no similar_items provided
    if not similar_items_list:
        return []
    # Fetch document of recommendations list from mongo
    popularity_items_list = list(
        rec_db_conn.get_database_instance()[collection_name].find(
            {"item_id": {"$in": similar_items_list}}, {"_id": 0}
        )
    )
    similar_items_df = pd.DataFrame(similar_items_list, columns=["item_id"])
    popularity_items_df = pd.DataFrame(popularity_items_list)

    # Merge similar_items with popularity_items based on item_id
    rec_df = similar_items_df.merge(popularity_items_df, how="left")

    # Impute the popularity score with 0 for the items where popularity score not found
    rec_df["score"].fillna(0, inplace=True)

    # Sort descending by score, and ascending by item_id
    rec_df.sort_values(
        by=["score", "item_id"],
        ascending=[False, True],
        inplace=True,
    )
    # Storing final recommendations as a list
    return rec_df["item_id"].tolist()


def get_picks_from_experts(
    featured_first_layer_category_by_user_model,
    popular_first_layer_category_model,
    **kwargs
):
    """
    This function gets n categories and k recommendations for each category.
    if user exists, it fetches n categories from featured_first_layer_category_by_user
    If user does not exist, or does not return enough results,
    fetches n categories from popular_first_layer_category
    then uses these categories to get k recommendations from popular_item_by_category collections.

    :param featured_first_layer_category_by_user_model: object. Model object for featured_first_layer_category_by_user
    :param popular_first_layer_category_model: object. Model object for popular_first_layer_category

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
    user_id = kwargs["user_id"]
    category_count = kwargs["category_count"]
    candidate_count = kwargs["candidate_count"]
    collection_name = kwargs["collection_name"]
    filter_args = {
        "table_name": kwargs["table_name"],
        "item_col_name": kwargs["item_col_name"],
        "check_col_name": kwargs["check_col_name"],
        "check_val": kwargs["check_val"],
        "db_connection": glb_db_conn,
    }
    # Adding a buffer to get additional categories from the collections
    # So that after filtering we can atleast get the original count
    category_buffer = kwargs["category_buffer"]

    try:
        featured_first_layer_category_object = (
            featured_first_layer_category_by_user_model.objects(user_id=user_id).get()
        )
        category_list = featured_first_layer_category_object.recommendations[
            : (category_count + category_buffer)
        ]

        # If not enough featured_first_layer_category returned,
        # add popular_first_layer_category objects to category_list
        if len(category_list) < category_count:
            popular_first_layer_category = _fetch_popular_first_layer_category(
                popular_first_layer_category_model, category_buffer + category_count
            )
            category_list.extend(popular_first_layer_category)
            category_list = list(OrderedDict.fromkeys(category_list))

    except DoesNotExist:
        try:
            category_list = _fetch_popular_first_layer_category(
                popular_first_layer_category_model, category_buffer + category_count
            )
        except DoesNotExist:
            raise NotEnoughRecommendations

    rec_df = general_picks_function(
        category_list=category_list,
        return_number=candidate_count,
        collection_name=collection_name,
        **filter_args,
    )
    result = (
        rec_df.head(category_count)
        .set_index("category_path")
        .to_dict()["recommendations"]
    )
    if len(result) < category_count:
        raise NotEnoughRecommendations

    return result


def _fetch_popular_first_layer_category(model, candidate_count):
    """
    A helper function to fetch popular_first_layer_category objects with candidate_count
    :param model: object. Model object for popular_first_layer_category
    :param candidate_count: int
    :return a recommendation list
    """
    try:
        popular_first_layer_category = model.objects(group_id=0).get()
    except DoesNotExist as e:
        raise e

    return popular_first_layer_category.recommendations[:candidate_count]


def get_image_url_by_categories(category_list: list, **kwargs):
    """
    This function is used to get image url from category list, set None for image url not found.
    :param category_list: list. A list of category
    :param collection_name: str. t3category_imageurl
    :param candidate_count: int. No. of returned items, default 5
    :return: a dict of {category: image}
    """
    candidate_count = kwargs["candidate_count"]
    collection_name = kwargs["collection_name"]

    # extract tire 3 category from original category path
    t3_category_list = []
    try:
        for category in category_list:
            t3_category_list.append(category.split("//")[4])
    except IndexError:
        raise IndexError("Index out of range")

    category_image_list = list(
        sch_db_conn.get_database_instance()[collection_name].find(
            {"category": {"$in": t3_category_list}}, {"_id": 0}
        )
    )
    cat_img_df = pd.DataFrame(category_image_list)
    cat_df = pd.DataFrame(t3_category_list, columns=["category"])
    if not category_image_list:
        cat_img_df["category"] = np.nan
        cat_img_df["image_url"] = np.nan

    # merge category list and image url
    cat_img_df = cat_img_df.merge(cat_df, on="category", how="right")
    # fill missing image url with None string
    cat_img_df.fillna("None", inplace=True)

    # get first candidate_count rows from dataframe
    result = cat_img_df.head(candidate_count).set_index("category").to_dict()
    return result["image_url"]
