import logging

import pandas as pd
import datetime
from pymongo.errors import PyMongoError


def filter_deactivated_items(
    recommendation_list: list,
    db_connection,
    table_name: str,
    item_col_name: str,
    check_col_name: str,
    check_val,
    return_number: int,
):
    """
    This function is used to filter deactivated items in a given recommendation list
    :param recommendation_list: list
        recommendation list to be filtered
    :param db_connection:
        Given db connection to do filtering
    :param table_name: str
        The name of target table to be searched
    :param item_col_name: str
        Based on specific column to search
    :param check_col_name: str
        Based on specific column to check val
    :param check_val: The val to be checked,
    can be a string ("Active") or a regex like {"$regex": "^A"}
    :param return_number:
    return the number of recommendations required after filtering
    :return: list
        The recommendation list after filtering
    """
    filter_result = []
    if len(recommendation_list) == 0:
        return filter_result
    # check if item_col and check_col exist
    # Commenting assertion lines below to verify performance improvement, because almost all APIs call this function
    # assert collection.find_one(
    #     {item_col_name: {"$exists": True}}
    # ), "item_col not existed"
    # assert collection.find_one(
    #     {check_col_name: {"$exists": True}}
    # ), "check_col not existed"
    try:
        # Get collection from connection object
        collection = db_connection.get_database_instance()[table_name]
        active_items_data = pd.DataFrame(
            list(
                collection.distinct(
                    item_col_name,
                    {
                        "$and": [
                            {item_col_name: {"$in": recommendation_list}},
                            {check_col_name: check_val},
                        ]
                    },
                )
            ),
            columns=[item_col_name],
        )
        if active_items_data.empty:
            return []
        # Create an index for sorting based on the recommendation list order
        sorterIndex = dict(zip(recommendation_list, range(len(recommendation_list))))
        # Generate a rank column based on the index for sorting
        active_items_data["rec_rank"] = active_items_data[item_col_name].map(
            sorterIndex
        )
        # sort by the same order as the rec_rank column
        active_items_data.sort_values(by=["rec_rank"], inplace=True)
        return active_items_data[item_col_name].tolist()[:return_number]
    # Adding PyMongoError for now because its the base exception class for pymongo errors
    except PyMongoError as e:
        logging.error(msg=f"Error: Connecting to glb_db_conn {e}")


def filter_deactivated_items_df(
    recommendation_df: pd.DataFrame,
    rec_col: str,
    return_number: int,
    db_connection,
    table_name: str,
    item_col_name: str,
    check_col_name: str,
    check_val,
):
    """
    This function is used to filter deactivated items in a given recommendation dataframe
    :param recommendation_df: pd.DataFrame
        recommendation dataframe to filter
    :param rec_col: str
        The recommendations column name in recommendation dataframe
    :param return_number: int
        number of recommendations for each item that will be returned
    :param db_connection:
        Given db connection to do filtering
    :param table_name: str
        The name of target table to be searched
    :param item_col_name: str
        Based on specific column to search
    :param check_col_name: str
        Based on specific column to check val
    :param check_val: The val to be checked,
    can be a string ("Active") or a regex like {"$regex": "^A"}
    :return: list
        The recommendation dataframe after filtering
    """

    # Convert recommendations column to list with unique values
    recommendations_unique_list = recommendation_df[rec_col].explode().unique().tolist()

    # Filter out inactive items
    active_recommendations_unique_list = filter_deactivated_items(
        recommendation_list=recommendations_unique_list,
        return_number=len(recommendations_unique_list),
        db_connection=db_connection,
        table_name=table_name,
        item_col_name=item_col_name,
        check_col_name=check_col_name,
        check_val=check_val,
    )

    # Add a temp column to store all active recommendations
    recommendation_df[rec_col] = recommendation_df[rec_col].apply(
        lambda x: [item for item in x if item in active_recommendations_unique_list][
            :return_number
        ]
    )

    return recommendation_df


def filter_deactivated_items_in_time_range(
    recommendation_list: list,
    db_connection,
    table_name: str,
    item_col_name: str,
    check_col_name: str,
    check_val,
    badges_name: str,
    badges_check_name: str,
    badges_check_val,
    current_time: datetime,
    badges_start_date_name: str,
    badges_expiration_date_name: str,
    return_number: int,
):
    """
    This function is used to filter deactivated items in a given recommendation list,
    with badges.sale or badges.clearance equals True
    with current timestamp in the range of (badges_start_date, badges_expiration_date)

    :param recommendation_list: list
        recommendation list to be filtered
    :param db_connection:
        Given db connection to do filtering
    :param table_name: str
        The name of target table to be searched
    :param item_col_name: str
        Based on specific column to search
    :param check_col_name: str
        Based on specific column to check val, e.g. status
    :param check_val:
        The val to be checked, e.g. 1 for activate status, 0 for inactivate
    :param badges_name:
        The badges name of a product: badges
    :param badges_check_name: str
        The badges check col name, e.g. clearance, sale
    :param badges_check_val:
        The badges val to be checked,
    :param current_time: datetime
        Timestamp query
    :param badges_start_date_name:
        The col name to query start time, e.g. badges.sale_start_date, clearance_start_date
    :param badges_expiration_date_name:
        The col name to query end time, e.g. badges.sale_expiration_date, clearance_expiration_date
    :param return_number: int
        return the number of recommendations required after filtering
    :return:
        The recommendation list after filtering
    """

    filter_result = []
    if len(recommendation_list) == 0:
        return filter_result
    # Get collection from connection object
    collection = db_connection.get_database_instance()[table_name]
    # check if item_col and check_col exist
    assert collection.find_one(
        {item_col_name: {"$exists": True}}
    ), "item_col not existed"
    assert collection.find_one(
        {check_col_name: {"$exists": True}}
    ), "check_col not existed"
    assert collection.find_one(
        {badges_name: {"$exists": True}}
    ), "badges_name not existed"

    badges_check_name = badges_name + "." + badges_check_name
    badges_start_date_name = badges_name + "." + badges_start_date_name
    badges_expiration_date_name = badges_name + "." + badges_expiration_date_name
    assert collection.find_one(
        {badges_check_name: {"$exists": True}}
    ), "badges_name.badges_check_name not existed"
    assert collection.find_one(
        {badges_start_date_name: {"$exists": True}}
    ), "badges_name.badges_start_date_name not existed"
    assert collection.find_one(
        {badges_expiration_date_name: {"$exists": True}}
    ), "badges_name.badges_expiration_date_name not existed"
    active_items_data = pd.DataFrame(
        list(
            collection.distinct(
                item_col_name,
                {
                    "$and": [
                        {item_col_name: {"$in": recommendation_list}},
                        {check_col_name: check_val},
                        {badges_check_name: badges_check_val},
                        {badges_start_date_name: {"$lt": current_time}},
                        {badges_expiration_date_name: {"$gt": current_time}},
                    ]
                },
            )
        ),
        columns=[item_col_name],
    )
    if active_items_data.empty:
        return []
    # Create an index for sorting based on the recommendation list order
    sorterIndex = dict(zip(recommendation_list, range(len(recommendation_list))))
    # Generate a rank column based on the index for sorting
    active_items_data["rec_rank"] = active_items_data[item_col_name].map(sorterIndex)
    # sort by the same order as the rec_rank column
    active_items_data.sort_values(by=["rec_rank"], inplace=True)
    return active_items_data[item_col_name].tolist()[:return_number]
