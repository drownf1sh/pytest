from flask_restplus import fields
import app.main.util.externalized_messages as messages
from app.main.util.global_vars import word_vector_length

"""
We keep all arguments for different controllers here, including the various error message.
"""
# list of common used args
args_list = {
    "store_id": {
        "type": int,
        "required": True,
        "help": messages.help["store_id"],
        "location": "args",
    },
    "spanner_table_name": {
        "type": str,
        "required": False,
        "help": messages.help["collection_name"],
        "location": "args",
        "default": "events",
    },
    "user_id_str": {
        "type": str,
        "required": True,
        "help": messages.help["user_id"],
        "location": "args",
    },
    "customer_email": {
        "type": str,
        "required": True,
        "help": messages.help["customer_email"],
        "location": "args",
    },
    "user_id": {
        "type": int,
        "required": True,
        "help": messages.help["user_id"],
        "location": "args",
    },
    "user_id_opt": {
        "type": int,
        "required": False,
        "help": messages.help["user_id_opt"],
        "location": "args",
        "default": 0,
    },
    "user_id_opt_str": {
        "type": str,
        "required": False,
        "help": messages.help["user_id_opt"],
        "location": "args",
        "default": "",
    },
    "category_count": {
        "type": int,
        "required": False,
        "help": messages.help["number_of_category"],
        "location": "args",
        "default": 5,
    },
    "category_buffer": {
        "type": int,
        "required": False,
        "help": messages.help["number_of_category_buffer"],
        "location": "args",
        "default": 5,
    },
    "item_id": {
        "type": str,
        "required": True,
        "help": messages.help["item_id"],
        "location": "args",
    },
    "zip_code": {
        "type": str,
        "required": True,
        "help": messages.help["zip_code"],
        "location": "args",
    },
    "external_id": {
        "type": str,
        "required": True,
        "help": messages.help["external_id"],
        "location": "args",
    },
    "event_id": {
        "type": int,
        "required": True,
        "help": messages.help["event_id"],
        "location": "args",
    },
    "event_id_str": {
        "type": str,
        "required": False,
        "help": messages.help["event_id"],
        "location": "args",
        "default": "event_id",
    },
    "event_type": {
        "type": str,
        "required": False,
        "help": messages.help["event_type"],
        "location": "args",
        "default": "ALL",
    },
    "event_type_str": {
        "type": str,
        "required": False,
        "help": messages.help["event_type"],
        "location": "args",
        "default": "event_type",
    },
    "event_date_str": {
        "type": str,
        "required": False,
        "help": "event date column",
        "location": "args",
        "default": "event_date",
    },
    "no_schedule_table_name": {
        "type": str,
        "required": False,
        "help": messages.help["collection_name"],
        "location": "args",
        "default": "arr_schedule",
    },
    "schedule_time_buffer": {
        "type": int,
        "required": False,
        "help": "added time buffer for events to show from current time",
        "location": "args",
        "default": 0,
    },
    "view_weight": {
        "type": float,
        "required": False,
        "help": messages.help["view_weight"],
        "location": "args",
        "default": 1.0,
    },
    "candidate_count": {
        "type": int,
        "required": False,
        "help": messages.help["number_of_rec"],
        "location": "args",
        "default": 5,
    },
    "ad_candidate_count": {
        "type": int,
        "required": False,
        "help": messages.help["number_of_ad_rec"],
        "location": "args",
        "default": 5,
    },
    "category_path": {
        "type": str,
        "required": True,
        "help": messages.help["category_path"],
        "location": "args",
    },
    "store_name": {
        "type": str,
        "required": True,
        "help": messages.help["store_name"],
        "location": "args",
    },
    "items_id_list": {
        "type": str,
        "required": True,
        "help": messages.help["items_id_list"],
        "location": "args",
    },
    "rec_item_ids": {
        "type": str,
        "required": False,
        "help": messages.help["rec_item_ids"],
        "location": "args",
    },
    "items_scores": {
        "type": str,
        "required": False,
        "help": messages.help["items_scores"],
        "location": "args",
    },
    "recently_viewed_streaming_user_id": {
        "type": str,
        "required": True,
        "help": messages.help["user_id"],
        "location": "args",
    },
    "recently_viewed_streaming_date_interval": {
        "type": int,
        "required": False,
        "help": "date_interval",
        "location": "args",
        "default": 30,
    },
    "items_id_list_search_rerank": fields.String(
        required=True, description=messages.descriptions["items_id_list"]
    ),
    "order_history_list": fields.String(
        required=True, description=messages.descriptions["order_history_list"]
    ),
    "order_history_weights": fields.String(
        required=False, description=messages.descriptions["order_history_weights"]
    ),
    "words": {
        "type": str,
        "required": True,
        "help": messages.help["words"],
        "location": "args",
        "action": "append",
    },
    "sentence": {
        "type": str,
        "required": True,
        "help": messages.help["sentence"],
        "location": "args",
        "action": "append",
    },
    "query_keyword": {
        "type": str,
        "required": True,
        "help": messages.help["query_keyword"],
        "location": "args",
    },
    "filter_inactive_items_args": {
        "db_name": {
            "type": str,
            "required": False,
            "help": "db name",
            "location": "args",
            "default": "mongo_glb",
        },
        "table_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "online_product",
        },
        "item_col_name": {
            "type": str,
            "required": False,
            "help": "item column name",
            "location": "args",
            "default": "sku_number",
        },
        "check_col_name": {
            "type": str,
            "required": False,
            "help": "check column name",
            "location": "args",
            "default": "status",
        },
        "check_val": {
            "type": int,
            "required": False,
            "help": "check number val",
            "location": "args",
            "default": 1,
        },
    },
    "filter_inactive_projects_args": {
        "project_db_name": {
            "type": str,
            "required": False,
            "help": "db name",
            "location": "args",
            "default": "mongo_glb",
        },
        "project_table_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "project_product",
        },
        "project_item_col_name": {
            "type": str,
            "required": False,
            "help": "item column name",
            "location": "args",
            "default": "external_id",
        },
        "project_check_col_name": {
            "type": str,
            "required": False,
            "help": "check column name",
            "location": "args",
            "default": "status",
        },
        "project_check_val": {
            "type": int,
            "required": False,
            "help": "check number val",
            "location": "args",
            "default": 1,
        },
    },
    "filter_archived_events_args": {
        "table_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "arr_events",
        },
        "archived_str": {
            "type": str,
            "required": False,
            "help": "archived name",
            "location": "args",
            "default": "archived",
        },
    },
    "michaels_badges_args": {
        "badges_name": {
            "type": str,
            "required": False,
            "help": "The badges object name of a product",
            "location": "args",
            "default": "badges",
        },
        "badges_sale_name": {
            "type": str,
            "required": False,
            "help": "sale name of a badges object",
            "location": "args",
            "default": "sale",
        },
        "badges_sale_val": {
            "type": bool,
            "required": False,
            "help": "sale value of a badges object",
            "location": "args",
            "default": True,
        },
        "badges_clearance_name": {
            "type": str,
            "required": False,
            "help": "clearance name of a badges object",
            "location": "args",
            "default": "clearance",
        },
        "badges_clearance_val": {
            "type": bool,
            "required": False,
            "help": "clearance value of a badges object",
            "location": "args",
            "default": True,
        },
        "badges_sale_start_date_name": {
            "type": str,
            "required": False,
            "help": "sale_start_date name of a badges object",
            "location": "args",
            "default": "sale_start_date",
        },
        "badges_sale_expiration_date_name": {
            "type": str,
            "required": False,
            "help": "sale expiration date name of a badges object",
            "location": "args",
            "default": "sale_expiration_date",
        },
        "badges_clearance_start_date_name": {
            "type": str,
            "required": False,
            "help": "clearance start date name of a badges object",
            "location": "args",
            "default": "clearance_start_date",
        },
        "badges_clearance_expiration_date_name": {
            "type": str,
            "required": False,
            "help": "clearance expiration date name of a badges object",
            "location": "args",
            "default": "clearance_expiration_date",
        },
    },
}

mktplace_args = {
    "similar_events_args": {
        "event_id": args_list["event_id"],
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["event_not_found_error"],
    },
    "similar_projects_args": {
        "external_id": args_list["external_id"],
        "error_message": messages.error_messages["project_not_found_error"],
    },
    "popular_products_in_events": {
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "trending_project_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "shopping_cart_bundle_args": {
        "items_id_list": args_list["items_id_list"],
        "purchased_together_collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "fgm_purchased_together",
        },
        "similar_items_collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "fgm_similar_items",
        },
        "redis_similar_items_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "fgm_similar_items",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "popular_visited_projects_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "popular_visited_items_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "popular_visited_events_args": {
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "upcoming_event": {
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["timestamp_not_found_error"],
    },
    "popular_products_in_projects": {
        "mik_channel": {
            "type": int,
            "required": False,
            "help": "mik channel for inventory platform",
            "location": "args",
            "default": 1,
        },
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "purchased_together_bundle_args": {
        "items_id_list": args_list["items_id_list"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "fgm_purchased_together",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "recommend_for_you_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "shop_near_you_args": {
        "zip_code": args_list["zip_code"],
        "error_message": messages.error_messages["zip_code_not_found_error"],
    },
    "you_may_also_buy_args": {
        "user_id": args_list["user_id_str"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "similar_items_args": {
        "item_id": args_list["item_id"],
        # "ad_candidate_count": args_list["ad_candidate_count"],
        "redis_similar_items_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "fgm_similar_items",
        },
        # "redis_similar_ad_items_hash_key": {
        #     "type": str,
        #     "required": False,
        #     "help": messages.help["redis_hash_key"],
        #     "location": "args",
        #     "default": "fgm_similar_ad_items",
        # },
        "similar_items_api": {
            "type": bool,
            "required": False,
            "help": messages.help["similar_items_api"],
            "location": "args",
            "default": True,
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "popular_item_args": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "event_for_you_args": {
        "user_id": args_list["user_id"],
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "trending_now_args": {
        "category_path": args_list["category_path"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
    },
    "trending_now_all_args": {
        "trending_now": {
            "type": str,
            "required": False,
            "help": "collection name",
            "location": "args",
            "default": "fgm_trending_now",
        },
        "user_defined_trending_now": {
            "type": str,
            "required": False,
            "help": "collection name",
            "location": "args",
            "default": "fgm_user_defined_trending_now",
        },
        "error_message": messages.error_messages["candidate_count_not_valid"],
    },
    "popular_search_keyword_args": {
        "error_message": messages.error_messages["candidate_count_not_valid"],
    },
    "rec_for_you_search_args": {
        "user_id": args_list["user_id_opt"],
        "error_message": messages.error_messages["candidate_count_not_valid"],
    },
    "search_term_categories_args": {
        "search_term": {
            "type": str,
            "required": True,
            "help": messages.help["search_term"],
            "location": "args",
        },
        "word_vector_length": {
            "type": int,
            "required": False,
            "help": messages.help["word_vector_length"],
            "location": "args",
            "default": word_vector_length,
        },
        "error_message": messages.error_messages["words_not_valid"],
    },
    "put_mktplace_similar_items_args": {
        "sku_number": {
            "type": str,
            "required": True,
            "help": messages.help["new_product_sku_number"],
            "location": "args",
        },
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "online_product",
        },
        "candidate_count": {
            "type": int,
            "required": False,
            "help": messages.help["number_of_rec"],
            "location": "args",
            "default": 20,
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "recently_viewed_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "popular_item_by_store_args": {
        "store_id": args_list["store_id"],
        "error_message": messages.error_messages["store_id_not_found_error"],
    },
    "popular_item_by_category_args": {
        "category_path": args_list["category_path"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
    },
    "recently_viewed_streaming_args": {
        "user_id": args_list["recently_viewed_streaming_user_id"],
        "date_interval": args_list["recently_viewed_streaming_date_interval"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "search_people_also_buy_args": {
        "items_id_list": args_list["items_id_list"],
        "items_scores": args_list["items_scores"],
        "error_message": messages.error_messages["item_not_found_error"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "fgm_people_also_buy",
        },
    },
    "top_picks_args": {
        "user_id": args_list["user_id_str"],
        "redis_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "fgm_streaming_top_picks",
        },
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "fgm_popular_item_by_category",
        },
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "search_rerank_args": {
        "items_id_list": args_list["items_id_list_search_rerank"],
        "order_history_list": args_list["order_history_list"],
        "order_history_weights": args_list["order_history_weights"],
        "redis_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "cbf_item_vector",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "put_user_defined_trending_now_args": {
        "category_path": args_list["category_path"],
        "rec_item_ids": args_list["rec_item_ids"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
    },
    "popular_event_args": {
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "popular_project_args": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "yesterday_popular_item_args": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "new_projects": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "favorite_item_args": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "trending_event_args": {
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "streaming_trending_now_list_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
        "redis_streaming_trending_now_list_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "fgm_streaming_trending_now_list",
        },
    },
    "popular_first_layer_category_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "people_also_buy_args": {
        "item_id": args_list["item_id"],
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "related_categories_by_category_args": {
        "category_path": args_list["category_path"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
    },
    "related_queries_by_category_args": {
        "category_path": args_list["category_path"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
    },
    "similar_items_by_popularity_args": {
        "item_id": args_list["item_id"],
        "redis_similar_items_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "fgm_similar_items",
        },
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "fgm_popular_master_items",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "related_queries_by_query_args": {
        "query_keyword": args_list["query_keyword"],
        "error_message": messages.error_messages["query_keyword_not_found_error"],
    },
    "related_categories_by_query_args": {
        "query_keyword": args_list["query_keyword"],
        "error_message": messages.error_messages["query_keyword_not_found_error"],
    },
    "picks_from_experts_args": {
        "user_id": args_list["user_id_opt"],
        "category_count": args_list["category_count"],
        "category_buffer": args_list["category_buffer"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "fgm_popular_item_by_category",
        },
        "error_message": messages.error_messages["count_not_valid"],
    },
    # put common used argument in common_args to reduce duplication
    "common_args": {
        "candidate_count": args_list["candidate_count"],
        "db_name": args_list["filter_inactive_items_args"]["db_name"],
        "table_name": args_list["filter_inactive_items_args"]["table_name"],
        "item_col_name": args_list["filter_inactive_items_args"]["item_col_name"],
        "check_col_name": args_list["filter_inactive_items_args"]["check_col_name"],
        "check_val": args_list["filter_inactive_items_args"]["check_val"],
        "project_db_name": args_list["filter_inactive_projects_args"][
            "project_db_name"
        ],
        "project_table_name": args_list["filter_inactive_projects_args"][
            "project_table_name"
        ],
        "project_item_col_name": args_list["filter_inactive_projects_args"][
            "project_item_col_name"
        ],
        "project_check_col_name": args_list["filter_inactive_projects_args"][
            "project_check_col_name"
        ],
        "project_check_val": args_list["filter_inactive_projects_args"][
            "project_check_val"
        ],
        "spanner_table_name": args_list["spanner_table_name"],
        "event_id_str": args_list["event_id_str"],
        "event_type_str": args_list["event_type_str"],
        "event_date_str": args_list["event_date_str"],
        "schedule_time_buffer": args_list["schedule_time_buffer"],
        "no_schedule_table_name": args_list["no_schedule_table_name"],
        "archived_str": args_list["filter_archived_events_args"]["archived_str"],
        "archived_event_table_name": args_list["filter_archived_events_args"][
            "table_name"
        ],
    },
}
for key in mktplace_args.keys():
    if key != "common_args" and key != "put_mktplace_similar_items_args":
        mktplace_args[key].update(mktplace_args["common_args"])

michaels_args = {
    "popular_products_in_events": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "shopping_cart_bundle_args": {
        "items_id_list": args_list["items_id_list"],
        "purchased_together_collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "mik_purchased_together",
        },
        "similar_items_collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "mik_similar_items",
        },
        "redis_similar_items_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "mik_similar_items",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "upcoming_event": {
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["timestamp_not_found_error"],
    },
    "popular_item_by_category_args": {
        "category_path": args_list["category_path"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
    },
    "popular_products_in_projects": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "trending_project_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "purchased_together_bundle_args": {
        "items_id_list": args_list["items_id_list"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "mik_purchased_together",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "viewed_together_args": {
        "item_id": args_list["item_id"],
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "popular_item_by_store_args": {
        "store_id": args_list["store_id"],
        "error_message": messages.error_messages["store_id_not_found_error"],
    },
    "recommend_for_you_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "you_may_also_buy_args": {
        "user_id": args_list["user_id_str"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "favorite_item_for_you_args": {
        "user_id": args_list["user_id_str"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "similar_items_args": {
        "item_id": args_list["item_id"],
        # "ad_candidate_count": args_list["ad_candidate_count"],
        "redis_similar_items_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "mik_similar_items",
        },
        # "redis_similar_ad_items_hash_key": {
        #     "type": str,
        #     "required": False,
        #     "help": messages.help["redis_hash_key"],
        #     "location": "args",
        #     "default": "mik_similar_ad_items",
        # },
        "similar_items_api": {
            "type": bool,
            "required": False,
            "help": messages.help["similar_items_api"],
            "location": "args",
            "default": True,
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "similar_ad_items_args": {
        "item_id": args_list["item_id"],
        "ad_candidate_count": args_list["ad_candidate_count"],
        "redis_similar_ad_items_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "mik_similar_ad_items",
        },
        "similar_items_api": {
            "type": bool,
            "required": False,
            "help": messages.help["similar_items_api"],
            "location": "args",
            "default": False,
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "purchased_and_viewed_together_args": {
        "item_id": args_list["item_id"],
        "view_weight": args_list["view_weight"],
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "purchased_together_args": {
        "item_id": args_list["item_id"],
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "trending_now_args": {
        "category_path": args_list["category_path"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
    },
    "trending_now_all_args": {
        "trending_now": {
            "type": str,
            "required": False,
            "help": "collection name",
            "location": "args",
            "default": "mik_trending_now",
        },
        "user_defined_trending_now": {
            "type": str,
            "required": False,
            "help": "collection name",
            "location": "args",
            "default": "mik_user_defined_trending_now",
        },
        "error_message": messages.error_messages["candidate_count_not_valid"],
    },
    "featured_category_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "buy_it_again_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "popular_search_keyword_args": {
        "error_message": messages.error_messages["candidate_count_not_valid"],
    },
    "rec_for_you_search_args": {
        "user_id": args_list["user_id_opt"],
        "error_message": messages.error_messages["candidate_count_not_valid"],
    },
    "people_also_buy_args": {
        "item_id": args_list["item_id"],
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "people_also_view_args": {
        "item_id": args_list["item_id"],
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "seasonal_top_picks_args": {
        "error_message": messages.error_messages["item_not_found_error"]
    },
    "top_picks_args": {
        "user_id": args_list["user_id_str"],
        "redis_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "mik_streaming_top_picks",
        },
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "mik_popular_item_by_category",
        },
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "popular_clearance_category_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "popular_visited_projects_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "popular_visited_items_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "popular_sale_category_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "popular_visited_events_args": {
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "recently_viewed_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "recently_viewed_streaming_args": {
        "user_id": args_list["recently_viewed_streaming_user_id"],
        "date_interval": args_list["recently_viewed_streaming_date_interval"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "project_use_this_args": {
        "item_id": args_list["item_id"],
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "project_inspiration_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "popular_item_args": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "similar_projects_args": {
        "external_id": args_list["external_id"],
        "error_message": messages.error_messages["project_not_found_error"],
    },
    "similar_items_for_bundle_args": {
        "items_id_list": args_list["items_id_list"],
        "redis_similar_items_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "mik_similar_items",
        },
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "mik_similar_items",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "event_for_you_args": {
        "user_id": args_list["user_id"],
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "similar_events_args": {
        "event_id": args_list["event_id"],
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["event_not_found_error"],
    },
    "popular_event_args": {
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "popular_category_args": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "popular_project_args": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "search_people_also_buy_args": {
        "items_id_list": args_list["items_id_list"],
        "items_scores": args_list["items_scores"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "mik_people_also_buy",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "search_rerank_args": {
        "items_id_list": args_list["items_id_list_search_rerank"],
        "order_history_list": args_list["order_history_list"],
        "order_history_weights": args_list["order_history_weights"],
        "redis_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "cbf_item_vector",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "put_user_defined_trending_now_args": {
        "category_path": args_list["category_path"],
        "rec_item_ids": args_list["rec_item_ids"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
    },
    "picks_from_experts_args": {
        "user_id": args_list["user_id_opt"],
        "category_count": args_list["category_count"],
        "category_buffer": args_list["category_buffer"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "mik_popular_item_by_category",
        },
        "error_message": messages.error_messages["count_not_valid"],
    },
    "yesterday_popular_item_args": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "new_projects": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "trending_event_args": {
        "event_type": args_list["event_type"],
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "popular_clearance_item_args": {
        "user_id": args_list["user_id_opt_str"],
        "redis_popular_clearance_item_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "mik_streaming_top_clearance",
        },
        "error_message": messages.error_messages["group_id_not_found_error"],
        "badges_name": args_list["michaels_badges_args"]["badges_name"],
        "badges_check_name": args_list["michaels_badges_args"]["badges_clearance_name"],
        "badges_check_val": args_list["michaels_badges_args"]["badges_clearance_val"],
        "badges_start_date_name": args_list["michaels_badges_args"][
            "badges_clearance_start_date_name"
        ],
        "badges_expiration_date_name": args_list["michaels_badges_args"][
            "badges_clearance_expiration_date_name"
        ],
    },
    "popular_sale_item_args": {
        "user_id": args_list["user_id_opt_str"],
        "redis_popular_sale_item_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "mik_streaming_top_sale",
        },
        "error_message": messages.error_messages["group_id_not_found_error"],
        "badges_name": args_list["michaels_badges_args"]["badges_name"],
        "badges_check_name": args_list["michaels_badges_args"]["badges_sale_name"],
        "badges_check_val": args_list["michaels_badges_args"]["badges_sale_val"],
        "badges_start_date_name": args_list["michaels_badges_args"][
            "badges_sale_start_date_name"
        ],
        "badges_expiration_date_name": args_list["michaels_badges_args"][
            "badges_sale_expiration_date_name"
        ],
    },
    "streaming_trending_now_list_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
        "redis_streaming_trending_now_list_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "mik_streaming_trending_now_list",
        },
    },
    "popular_first_layer_category_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
    },
    "similar_items_in_same_store_args": {
        "item_id": args_list["item_id"],
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "related_categories_by_category_args": {
        "category_path": args_list["category_path"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "t3category_imageurl",
        },
    },
    "related_queries_by_category_args": {
        "category_path": args_list["category_path"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
    },
    "similar_items_by_popularity_args": {
        "item_id": args_list["item_id"],
        "redis_similar_items_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "mik_similar_items",
        },
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "mik_popular_master_items",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "related_queries_by_query_args": {
        "query_keyword": args_list["query_keyword"],
        "error_message": messages.error_messages["query_keyword_not_found_error"],
    },
    "related_categories_by_query_args": {
        "query_keyword": args_list["query_keyword"],
        "error_message": messages.error_messages["query_keyword_not_found_error"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "t3category_imageurl",
        },
    },
    # put common used argument in common_args to reduce duplication
    "common_args": {
        "candidate_count": args_list["candidate_count"],
        "db_name": args_list["filter_inactive_items_args"]["db_name"],
        "table_name": args_list["filter_inactive_items_args"]["table_name"],
        "item_col_name": args_list["filter_inactive_items_args"]["item_col_name"],
        "check_col_name": args_list["filter_inactive_items_args"]["check_col_name"],
        "check_val": args_list["filter_inactive_items_args"]["check_val"],
        "project_db_name": args_list["filter_inactive_projects_args"][
            "project_db_name"
        ],
        "project_table_name": args_list["filter_inactive_projects_args"][
            "project_table_name"
        ],
        "project_item_col_name": args_list["filter_inactive_projects_args"][
            "project_item_col_name"
        ],
        "project_check_col_name": args_list["filter_inactive_projects_args"][
            "project_check_col_name"
        ],
        "project_check_val": args_list["filter_inactive_projects_args"][
            "project_check_val"
        ],
        "spanner_table_name": args_list["spanner_table_name"],
        "event_id_str": args_list["event_id_str"],
        "event_type_str": args_list["event_type_str"],
        "event_date_str": args_list["event_date_str"],
        "schedule_time_buffer": args_list["schedule_time_buffer"],
        "no_schedule_table_name": args_list["no_schedule_table_name"],
        "archived_str": args_list["filter_archived_events_args"]["archived_str"],
        "archived_event_table_name": args_list["filter_archived_events_args"][
            "table_name"
        ],
    },
}
for key in michaels_args.keys():
    if key != "common_args":
        michaels_args[key].update(michaels_args["common_args"])

crm_args = {
    "personalized_scores_args": {
        "customer_email": args_list["customer_email"],
        "error_message": messages.error_messages["customer_email_not_found_error"],
    },
}


b2b_args = {
    "b2b_edu_purchased_together_bundle_args": {
        "items_id_list": args_list["items_id_list"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "b2b_edu_purchased_together",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "b2b_ent_purchased_together_bundle_args": {
        "items_id_list": args_list["items_id_list"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "b2b_ent_purchased_together",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "recommend_for_you_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "you_may_also_buy_args": {
        "user_id": args_list["user_id_str"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "trending_now_args": {
        "category_path": args_list["category_path"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
    },
    "purchased_together_args": {
        "item_id": args_list["item_id"],
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "similar_items_args": {
        "item_id": args_list["item_id"],
        # "ad_candidate_count": args_list["ad_candidate_count"],
        "redis_similar_items_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "b2b_similar_items",
        },
        # "redis_similar_ad_items_hash_key": {
        #     "type": str,
        #     "required": False,
        #     "help": messages.help["redis_hash_key"],
        #     "location": "args",
        #     "default": "b2b_similar_ad_items",
        # },
        "similar_items_api": {
            "type": bool,
            "required": False,
            "help": messages.help["similar_items_api"],
            "location": "args",
            "default": True,
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "featured_category_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "buy_it_again_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "popular_search_keyword_args": {
        "error_message": messages.error_messages["candidate_count_not_valid"],
    },
    "rec_for_you_search_args": {
        "user_id": args_list["user_id_opt"],
        "error_message": messages.error_messages["candidate_count_not_valid"],
    },
    "people_also_buy_args": {
        "item_id": args_list["item_id"],
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "seasonal_top_picks_args": {
        "error_message": messages.error_messages["item_not_found_error"]
    },
    "recently_viewed_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "recently_viewed_streaming_args": {
        "user_id": args_list["recently_viewed_streaming_user_id"],
        "date_interval": args_list["recently_viewed_streaming_date_interval"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "project_use_this_args": {
        "item_id": args_list["item_id"],
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "project_inspiration_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "popular_item_args": {
        "error_message": messages.error_messages["group_id_not_found_error"]
    },
    "event_for_you_args": {
        "user_id": args_list["user_id"],
        "error_message": messages.error_messages["user_id_not_found_error"],
    },
    "b2b_ent_trending_now_all_args": {
        "trending_now": {
            "type": str,
            "required": False,
            "help": "collection name",
            "location": "args",
            "default": "b2b_ent_trending_now",
        },
        "user_defined_trending_now": {
            "type": str,
            "required": False,
            "help": "collection name",
            "location": "args",
            "default": "b2b_ent_user_defined_trending_now",
        },
        "error_message": messages.error_messages["candidate_count_not_valid"],
    },
    "b2b_edu_trending_now_all_args": {
        "trending_now": {
            "type": str,
            "required": False,
            "help": "collection name",
            "location": "args",
            "default": "b2b_edu_trending_now",
        },
        "user_defined_trending_now": {
            "type": str,
            "required": False,
            "help": "collection name",
            "location": "args",
            "default": "b2b_edu_user_defined_trending_now",
        },
        "error_message": messages.error_messages["candidate_count_not_valid"],
    },
    "edu_search_people_also_buy_args": {
        "items_id_list": args_list["items_id_list"],
        "items_scores": args_list["items_scores"],
        "error_message": messages.error_messages["item_not_found_error"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "b2b_edu_people_also_buy",
        },
    },
    "ent_search_people_also_buy_args": {
        "items_id_list": args_list["items_id_list"],
        "items_scores": args_list["items_scores"],
        "error_message": messages.error_messages["item_not_found_error"],
        "collection_name": {
            "type": str,
            "required": False,
            "help": messages.help["collection_name"],
            "location": "args",
            "default": "b2b_ent_people_also_buy",
        },
    },
    "search_rerank_args": {
        "items_id_list": args_list["items_id_list_search_rerank"],
        "order_history_list": args_list["order_history_list"],
        "order_history_weights": args_list["order_history_weights"],
        "redis_hash_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "cbf_item_vector",
        },
        "error_message": messages.error_messages["item_not_found_error"],
    },
    "put_user_defined_trending_now_args": {
        "category_path": args_list["category_path"],
        "rec_item_ids": args_list["rec_item_ids"],
        "error_message": messages.error_messages["cat_path_not_found_error"],
    },
    "b2b_ent_streaming_trending_now_list_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
        "redis_streaming_trending_now_list_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "b2b_ent_streaming_trending_now_list",
        },
    },
    "b2b_edu_streaming_trending_now_list_args": {
        "error_message": messages.error_messages["group_id_not_found_error"],
        "redis_streaming_trending_now_list_key": {
            "type": str,
            "required": False,
            "help": messages.help["redis_hash_key"],
            "location": "args",
            "default": "b2b_edu_streaming_trending_now_list",
        },
    },
    # put common used argument in common_args to reduce duplication
    "common_args": {
        "candidate_count": args_list["candidate_count"],
        "db_name": args_list["filter_inactive_items_args"]["db_name"],
        "table_name": args_list["filter_inactive_items_args"]["table_name"],
        "item_col_name": args_list["filter_inactive_items_args"]["item_col_name"],
        "check_col_name": args_list["filter_inactive_items_args"]["check_col_name"],
        "check_val": args_list["filter_inactive_items_args"]["check_val"],
        "project_db_name": args_list["filter_inactive_projects_args"][
            "project_db_name"
        ],
        "project_table_name": args_list["filter_inactive_projects_args"][
            "project_table_name"
        ],
        "project_item_col_name": args_list["filter_inactive_projects_args"][
            "project_item_col_name"
        ],
        "project_check_col_name": args_list["filter_inactive_projects_args"][
            "project_check_col_name"
        ],
        "project_check_val": args_list["filter_inactive_projects_args"][
            "project_check_val"
        ],
    },
}
for key in b2b_args.keys():
    if key != "common_args":
        b2b_args[key].update(b2b_args["common_args"])

store_name_args = {
    "store_name": args_list["store_name"],
    "candidate_count": args_list["candidate_count"],
    "error_message": messages.error_messages["store_name_not_valid"],
    "Authorization": {
        "type": str,
        "required": True,
        "help": messages.help["fgm_token"],
        "location": "headers",
    },
    "min_name_length": {
        "type": int,
        "required": False,
        "help": messages.help["min_name_length"],
        "location": "args",
        "default": 6,
    },
    "max_name_length": {
        "type": int,
        "required": False,
        "help": messages.help["max_name_length"],
        "location": "args",
        "default": 20,
    },
    "name_cutoff_length": {
        "type": int,
        "required": False,
        "help": messages.help["name_cutoff_length"],
        "location": "args",
        "default": 15,
    },
}

word_embedding_args = {
    "words": args_list["words"],
    "error_message": messages.error_messages["words_not_valid"],
}

sentence_embedding_args = {
    "sentence": args_list["sentence"],
    "error_message": messages.error_messages["sentence_not_valid"],
}
