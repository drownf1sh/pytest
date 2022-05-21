import time
import pandas as pd

from app.main import rec_db_conn

# from app.main.configuration.vault_vars_config import (
#     SPANNER_INSTANCE_ID,
#     SPANNER_DATABASE_ID,
# )
# from app.main.util.global_db_connection import spanner_client


# def filter_archived_events(
#     recommendation_list: list,
#     table_name: str,
#     event_type_col: str,
#     return_number: int,
# ):
#     """
#     This function was used to filter archived events in Google Spanner from a given
#     recommendation list.
#     Currently it's deprecated because of the low performance to query data from
#     spanner and we already have a kafka pipeline to sync data from spanner to mongodb
#
#     :param recommendation_list: list
#         recommendation list to be filtered
#     :param table_name: str
#         spanner events table name for filtering
#     :param event_type_col: The type of event to be filtered
#     :param return_number: int
#         number of final recommendation results
#     :return: list
#         The recommendation list after filtering
#     """
#     filter_result = []
#     if len(recommendation_list) == 0:
#         return filter_result
#     # map input to int list
#     rec_list = list(map(int, recommendation_list))
#     # Converts event_type to upper
#     event_type_col = event_type_col.upper()
#     query_string = (
#         f"SELECT event_id"
#         f" FROM `{table_name}` "
#         f" INNER JOIN "
#         f" (SELECT * FROM UNNEST ({rec_list}) AS element WITH OFFSET AS offset) "
#         f" ON {table_name}.event_id = element "
#         f" AND {table_name}.archived=0 "
#     )
#     # return all if not among these
#     if event_type_col not in ("ONLINE", "PROJECT", "IN_STORE"):
#         query_string += " ORDER BY offset "
#     else:
#         query_string += (
#             f" AND {table_name}.event_type='{event_type_col}' ORDER BY offset "
#         )
#     # Get a Cloud Spanner instance by ID.
#     instance = spanner_client.instance(SPANNER_INSTANCE_ID)
#     # Get a Cloud Spanner database by ID.
#     database = instance.database(SPANNER_DATABASE_ID)
#     # Execute an SQL statement with error handling
#     try:
#         with database.snapshot() as snapshot:
#             resultset = snapshot.execute_sql(query_string)
#             filter_result = [column for row in resultset for column in row]
#     except GoogleAPICallError:
#         abort(500)
#
#     return filter_result[:return_number]


def filter_archived_events_in_mongo(
    recommendation_list: list,
    event_type_col: str,
    return_number: int,
    **kwargs,
):
    """
    This function is used to filter archived events in mongodb rec_dev00.arr_events table
    from a given recommendation list.
    :param recommendation_list: list
        recommendation list to be filtered
    :param event_type_col: The type of event to be filtered
    :param return_number: int
        number of final recommendation results

    Parameters used to filter archived events
    :param event_id: str
        string "event_id" used to filter in a db document
    :param event_type: str
        string "event_type" used to filter in a db document
    :param archived: str
        string "archived" used to filter in a db document
    :param db_connection:
        Given db connection to do filtering
    :param archived_event_table_name: str
        table name used to search events results
    :return: list
        The recommendation list after filtering
    """
    filter_result = []
    if len(recommendation_list) == 0:
        return filter_result

    event_id = kwargs["event_id_str"]
    event_type = kwargs["event_type_str"]
    archived = kwargs["archived_str"]
    db_connection = kwargs["db_connection"]
    archived_event_table_name = kwargs["archived_event_table_name"]

    # Get collection from connection object
    collection = db_connection.get_database_instance()[archived_event_table_name]
    # check if archived, event_id, event_type exist
    # removed for tps improvement
    # assert collection.find_one({archived: {"$exists": True}}), "archived not existed"
    # assert collection.find_one({event_id: {"$exists": True}}), "event_id not existed"
    # assert collection.find_one(
    #     {event_type: {"$exists": True}}
    # ), "event_type not existed"

    event_type_default = ["ONLINE", "PROJECT", "IN_STORE"]
    if event_type_col == "ALL" or event_type_col not in event_type_default:
        event_type_list = event_type_default
    else:
        event_type_list = list([event_type_col])

    recommendation_list = list(map(int, recommendation_list))

    active_events = pd.DataFrame(
        list(
            collection.distinct(
                event_id,
                {
                    "$and": [
                        {archived: 0},
                        {event_type: {"$in": event_type_list}},
                        {event_id: {"$in": recommendation_list}},
                    ]
                },
            )
        ),
        columns=[event_id],
    )
    # Create an index for sorting based on the recommendation list order
    sort_index = dict(zip(recommendation_list, range(len(recommendation_list))))
    # Generate a rank column based on the index for sorting
    active_events["rec_rank"] = active_events[event_id].map(sort_index)
    # sort by the same order as the rec_rank column
    active_events.sort_values(by=["rec_rank"], inplace=True)
    return (active_events[event_id]).tolist()[:return_number]


def filter_no_schedule_events_in_mongo(
    recommendation_list: list,
    return_number: int,
    **kwargs,
):
    """
    This function is used to filter events that have no schedule after the current
    time in mongodb rec_dev00.arr_schedule table from a given recommendation list.
    :param recommendation_list: list
        recommendation list to be filtered
    :param return_number: int
        number of final recommendation results

    Parameters used to filter archived events
    :param event_id_str: str
        string "event_id" column name used to filter in a db document
    :param event_date_str: str
        string "event_date" column name used to filter in a db document
    :param db_connection:
        Given db connection to do filtering
    :param no_schedule_table_name: str
        table name used to search schedule events results
    :param schedule_time_buffer: int
        a buffer to check if the events are available with atleast later than current_time + buffer
    :return: list
        The recommendation list after filtering
    """
    filter_result = []
    if len(recommendation_list) == 0:
        return filter_result

    event_id = kwargs["event_id_str"]
    event_date = kwargs["event_date_str"]
    no_schedule_table_name = kwargs["no_schedule_table_name"]
    schedule_time_buffer = kwargs["schedule_time_buffer"]
    db_connection = kwargs["db_connection"]
    # Get collection from connection object
    collection = db_connection.get_database_instance()[no_schedule_table_name]
    # removed for tps improvement
    # assert collection.find_one(
    #     {event_date: {"$exists": True}}
    # ), "event_date column does not exist"
    # assert collection.find_one(
    #     {event_id: {"$exists": True}}
    # ), "event_id column does not exist"
    recommendation_list = list(map(int, recommendation_list))
    current_time_in_millis = time.time_ns() // 1_000_000
    schedule_events = pd.DataFrame(
        list(
            collection.distinct(
                event_id,
                {
                    "$and": [
                        {event_id: {"$in": recommendation_list}},
                        {
                            event_date: {
                                "$gte": current_time_in_millis + schedule_time_buffer
                            }
                        },
                    ]
                },
            )
        ),
        columns=[event_id],
    )
    # Create an index for sorting based on the recommendation list order
    sort_index = dict(zip(recommendation_list, range(len(recommendation_list))))
    # Generate a rank column based on the index for sorting
    schedule_events["rec_rank"] = schedule_events[event_id].map(sort_index)
    # sort by the same order as the rec_rank column
    schedule_events.sort_values(by=["rec_rank"], inplace=True)
    return (schedule_events[event_id]).tolist()[:return_number]
