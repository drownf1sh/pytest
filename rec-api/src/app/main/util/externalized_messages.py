"""
All messages/strings should be kept in app.main.util.externalized_messages.py to make the maintenance easier.
You can name the key whatever you want as long as it's short and makes sense.

Before adding any new externalized string, PLEASE search the key first to make sure we don't have existing same key
under the same parent category. It's OK to have same key under different categories.
"""

error_messages = {
    "customer_email_not_found_error": "Error: Customer_email not found",
    "user_id_not_found_error": "Error: User ID not found",
    "zip_code_not_found_error": "Error: Please provide valid zip code",
    "item_not_found_error": "Error: Item ID not found",
    "project_not_found_error": "Error: Project ID not found",
    "event_not_found_error": "Error: Event ID not found",
    "internal_error": "Error: API internal error",
    "cat_path_not_found_error": "Error: Category path not found",
    "group_id_not_found_error": "Error: Group id not Found",
    "store_name_not_valid": "Error: Please provide a valid store name",
    "words_not_valid": "Error: Please provide valid words",
    "sentence_not_valid": "Error: Please provide valid sentence",
    "candidate_count_not_valid": "Error: Please provide valid candidate count",
    "count_not_valid": "Error: Please provide valid count",
    "unauthorized_access": "Unauthorized access",
    "store_id_not_found_error": "Error: Store ID not found",
    "timestamp_not_found_error": "Error: Timestamp not found",
    "value_error": "Input Parameters Value Error",
    "assertion_error": "Assertion Error",
    "not_enough_recommendations": "Not enough recommendations",
    "query_keyword_not_found_error": "Error: Query keyword not Found",
    "index_error": "Index out of range",
}

success_messages = {
    "return_list_success_with_value": "Success: Return a list of recommendation results \nExample Value: \n",
    "return_word_vector_json": "Success: Return a json data of words and vectors \nExample Value: \n",
    "return_phrase_list": "Success: Return a list of ngrams \nExample Value: \n",
    "return_sentence_vector": "Success: Return average vector of given sentence in json format \nExample Value: \n",
}

descriptions = {
    "customer_email": "Customer_email - REQUIRED",
    "number_of_recommended_item_5": "Number of recommended items to return, OPTIONAL: default to 5",
    "number_of_recommended_non_ad_item_5": "Number of recommended non-ad items to return, OPTIONAL: default to 5",
    "number_of_recommended_ad_item_5": "Number of recommended ad items to return, OPTIONAL: default to 5",
    "number_of_recommended_projects_5": "Number of recommended projects to return, OPTIONAL: default to 5",
    "number_of_recommended_events_5": "Number of recommended events to return, OPTIONAL: default to 5",
    "number_of_recommended_shops_5": "Number of recommended shops to return, OPTIONAL: default to 5",
    "number_of_recommended_categories_5": "Number of recommended categories to return, OPTIONAL: default to 5",
    "number_of_recommended_search_term_5": "Number of recommended search terms to return, OPTIONAL: default to 5",
    "user_id": "User ID - REQUIRED",
    "item_id": "Item ID - REQUIRED",
    "event_id": "Event ID - REQUIRED",
    "event_type": "Event type: ONLINE, IN_STORE, PROJECT or ALL, default to ALL - OPTIONAL",
    "zip_code": "Zip Code - REQUIRED",
    "new_product_sku_number": "New product sku number - REQUIRED",
    "external_id": "External ID - REQUIRED",
    "category_path": "Category path to be used - REQUIRED",
    "store_name": "Store Name - REQUIRED",
    "number_of_store_names": "Number of Suggested Store Names - OPTIONAL: default to 5",
    "search_term": "Search Term - REQUIRED",
    "view_weight": "View Weight - Weight specified to viewed_together recommendations, OPTIONAL: default to 1.0",
    "words": 'words list, e.g. "word apple orange" (split each word by a space) - REQUIRED',
    "words_ngram": 'words list, e.g. "apple_pie orange_pie" (split each ngram by a space) - REQUIRED',
    "sentence": 'a sentence string, e.g. "How are you today" (split each word by a space) - REQUIRED',
    "sentence_for_phrase": 'a sentence string, e.g. "this natural cotton sateen is environmentally friendly" (split each word by a space) - REQUIRED',
    "sentence_ngram": 'a sentence string, e.g. "I like reading comic_book" (split each ngram by a space) - REQUIRED',
    "items_id_list": "Items ID list. Splitted by space - REQUIRED",
    "items_scores": "Items Scores. Splitted by space - OPTIONAL default to 1",
    "order_history_list": "Order History of Items IDs. Splitted by space - REQUIRED",
    "order_history_weights": "Weights of Order History items. Splitted by space - OPTIONAL default to all 1s",
    "fgm_token": "The FGM user's token to access FGM APIs - REQUIRED",
    "rec_item_ids": "The list of recommended item ids. Splitted by space, REQUIRED",
    "store_id": "Store ID - REQUIRED",
    "query_keyword": "Query keywords used to get related queries - REQUIRED",
}

help = {
    "customer_email": "Customer email is required",
    "user_id": "User ID is required",
    "user_id_opt": "User ID is optional",
    "zip_code": "Zip Code is required",
    "number_of_category": "Number of category count must be int",
    "number_of_category_buffer": "Number of category buffer count must be int",
    "number_of_rec": "Number of recommend items must be int",
    "number_of_ad_rec": "Number of recommend ad items must be int",
    "item_id": "Item ID is required",
    "new_product_sku_number": "New product sku number is required",
    "external_id": "External ID is required",
    "event_id": "Event ID is required",
    "event_type": "Event type is optional",
    "percentage_of_rec": "Percentage of recommended items must be float",
    "category_path": "Category path is required",
    "store_name": "Store Name is required",
    "view_weight": "View Weight is optional, defaults to 1.0",
    "number_of_store_names": "Number of Suggested Store Names",
    "search_term": "Search Term is required",
    "words": "Words required",
    "sentence": "Sentence string required",
    "word_vector_length": "The vector dimension for word embedding",
    "items_id_list": "Items ID list is required",
    "items_scores": "Items Scores is optional",
    "order_history_list": "Order History of Items IDs is required",
    "fgm_token": "The FGM user's token is required",
    "rec_item_ids": "The recommended item ids if not specified is empty",
    "collection_name": "MongoDB collection name",
    "store_id": "Store ID is required",
    "similar_items_api": "Whether this is args for similar_items API",
    "min_name_length": "The min length of suggested store name",
    "max_name_length": "The max length of suggested store name",
    "name_cutoff_length": "The cutoff length of initial input store name",
    "redis_hash_key": "Redis hash key",
    "query_keyword": "Query keyword is required to get related queries",
}

example_format = {
    "phrase_value": '["this", "natural_cotton_sateen", "is", "environmentally_friendly”]',
    "word_embedding_value": '{"word": [0.01, 0.01, 0.01], "apple": [0.03, 0.03, 0.03], "orange": [0.02,0.02,0.02]}',
    "ngram_word_embedding_value": '{"apple_pie": [0.03, 0.03, 0.03], "orange_pie": [0.02,0.02,0.02]}',
    "sentence_embedding_value": '{"sentence": "How are you today", "vector": [0.01, 0.02, 0.03]}',
    "sentence_embedding_value_ngram": '{"sentence": "I like reading comic_book", "vector": [0.01, 0.02, 0.03]}',
    "general_recommendation_value": "[\n'10621943', \n '10610961', \n  '10610964', "
    "\n  '10624522', \n  '10610552'\n]",
    "search_term_cagetories": '[\n"Art Supplies//Paint & Painting Supplies//Paint",'
    ' \n"Papercraft//Card Making//Inks & Accessories",'
    ' \n"Crafts & Hobbies//Craft Paint//Acrylic Craft",'
    ' \n"Holiday Decor//Christmas//Christmas Ribbon",'
    " \n Crafts & Hobbies//Adhesives//Fabric Glue"
    " \n]",
    "store_name_suggestion": "[\n 'John Store',"
    " \n 'J Store',"
    " \n 'John Shop',"
    " \n 'J Shop',"
    " \n 'John Design',"
    " \n]",
    "personalized_scores_suggestion": "[\n 'customer_email': 'email_str',"
    " \n 'Flag_a': '1',"
    " \n 'Flag_b': '2',"
    " \n]",
    "new_product_similar_items": "["
    "\n {"
    "\n 'item_id': '10001',"
    "\n 'same_cluster_recommendations':['10002', '10003'],"
    "\n 'diff_cluster_recommendations':['20002', '20003']"
    "\n }"
    "\n]",
    "new_user_defined_trending_now": "["
    "\n {"
    "\n 'category_path': 'root//Frames'"
    "\n 'rec_item_ids': '134526 127645'"
    "\n }"
    "\n]",
}


def generate_api_responses(
    not_found_message,
    example_value=example_format["general_recommendation_value"],
    success_str="return_list_success_with_value",
):
    responses = {
        200: success_messages[success_str] + example_value,
        404: not_found_message,
        500: error_messages["internal_error"],
    }
    return responses
