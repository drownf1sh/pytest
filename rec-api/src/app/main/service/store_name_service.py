from app.main.components.dup_store_name_handler import (
    split_string_to_words,
    process_human_names,
    generate_suggested_names,
)
from app.main.components.synonyms_api import process_non_human_names


def get_store_name_suggestions(**kwargs):
    """
    :param kwargs:
    :return: Suggested similar store names
    """
    store_name = kwargs["store_name"]
    candidate_count = kwargs["candidate_count"]
    fgm_token = kwargs["Authorization"]
    min_name_length = kwargs["min_name_length"]
    max_name_length = kwargs["max_name_length"]
    name_cutoff_length = kwargs["name_cutoff_length"]
    # String process
    # Step 1.Split store name string to words - DONE
    human_names, non_human_names = split_string_to_words(store_name)

    # Words process
    # Step 2.Detect human name - DONE
    # Step 2a.For human name, get initials or abbreviation - DONE
    processed_words = process_human_names(human_names)
    # Step 2b.For non-human name, get synonyms - Done
    processed_words.extend(process_non_human_names(non_human_names))
    # Step 3.Apply profanity screening API - Done
    # Generate suggestions
    # Step 4.Combine screened strings together - Done
    # Step 5.Filter out existing suggested names - Done
    # Suggested amount and return
    # Step 6.If generated suggested is less than required, add suffixes - Done
    # Step 7.Return result - Done
    suggested_names = generate_suggested_names(
        store_name,
        processed_words,
        fgm_token=fgm_token,
        candidate_count=candidate_count,
        min_name_length=min_name_length,
        max_name_length=max_name_length,
        name_cutoff_length=name_cutoff_length,
    )
    return suggested_names
