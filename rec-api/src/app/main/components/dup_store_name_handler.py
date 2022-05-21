import time
from itertools import product, compress

import requests
import wordninja
from werkzeug.exceptions import Unauthorized

from app.main import names_set
from app.main.components.store_names import store_names_client
from app.main.configuration.vault_vars_config import (
    PROFANITY_SCREEN_API,
    STORE_NAME_DUP_CHECK_API,
)
from app.main.util.global_vars import user_agent


def split_string_to_words(store_name: str, check_human_name: bool = True):
    """
    :param store_name:
    :param check_human_name:
    :return:
    """
    assert isinstance(store_name, str), "store_name must be String"
    assert isinstance(check_human_name, bool), "check_human_name must be bool"
    words = wordninja.split(store_name.lower())
    human_names = []
    non_human_names = []
    for word in words:
        if check_human_name and (
            names_set.search_first_name(word) or names_set.search_last_name(word)
        ):
            human_names.append(word)
        else:
            non_human_names.append(word)

    if check_human_name:
        return human_names, non_human_names
    else:
        return non_human_names


def process_human_names(human_names: list):
    """
    :param human_names:
    :return:
    """
    assert isinstance(human_names, list), "human_names must be list"
    processed_human_names = []
    for human_name in human_names:
        # Get initial of human name
        initial = human_name[:1].upper()
        # Get abbreviation of human name for name longer than 4 chars
        # Currently we set the similarity score of initial as .998, and abbreviation as .999
        abbreviated_human_name = _abbreviate_human_name(human_name)
        if len(human_name) > 4 and abbreviated_human_name != human_name:
            processed_human_names.extend(
                [
                    {
                        human_name.title(): 1,
                        _abbreviate_human_name(human_name).title(): 0.999,
                        initial.title(): 0.998,
                    }
                ]
            )
        else:
            processed_human_names.extend(
                [{human_name.title(): 1, initial.title(): 0.998}]
            )
    return processed_human_names


def _abbreviate_human_name(name: str):
    if len(name) <= 4:
        return name
    abbreviation = name
    for i in range(4, 7):
        if names_set.search_first_name(name[:i]):
            abbreviation = name[:i]
            break
        if names_set.search_last_name(name[:i]):
            abbreviation = name[:i]
            break
    return abbreviation


def profanity_screen_word(synonyms_list: list, fgm_token: str):
    """
    Parameters
    ----------
    synonyms_list: list
        The synonyms names list
    fgm_token: str
        The token generated when user logs in

    Return
    ------
    filtered_synonyms_list: list
        The profanity screened synonyms names list
    """
    assert isinstance(synonyms_list, list), "synonyms_list must be list"
    words = []
    for synonyms in synonyms_list:
        words.extend(synonyms.keys())
    # Apply profanity screening API and return boolean list as result
    if not fgm_token.startswith("Bearer "):
        fgm_token = f"Bearer {fgm_token}"
    responses = requests.put(
        PROFANITY_SCREEN_API,
        json=words,
        headers={"Authorization": fgm_token, "User-Agent": user_agent},
    ).json()

    if "status" in responses.keys():
        raise AssertionError(f"{PROFANITY_SCREEN_API} api error")

    result = [response["result"] for response in responses["data"]]
    # Use the boolean list to filter out invalid words
    filtered_words = list(compress(words, result))
    filtered_synonyms_list = []
    for synonyms in synonyms_list:
        filtered_synonyms_list.append(
            {k: v for k, v in synonyms.items() if k in filtered_words}
        )

    return filtered_synonyms_list


def _filter_existing_names(suggested_names: list, fgm_token: str):
    """
    Pamameters
    ----------
    suggested_names: list
        The suggested names list
    fgm_token: str
        The token generated when user logs in

    Return
    ------
    suggested_name: list
        Suggested store names
    """
    assert isinstance(suggested_names, list), "suggested_names must be list"
    response = requests.post(
        STORE_NAME_DUP_CHECK_API,
        json={"suggestStoreNames": suggested_names},
        headers={"Authorization": fgm_token, "User-Agent": user_agent},
    )
    response_data = response.json()["data"]
    if not response_data:
        raise Unauthorized(response.json()["message"])

    duplicate_store_names = response_data["duplicateStoreNames"]
    return [name for name in suggested_names if name not in duplicate_store_names]


def generate_suggested_names(
    store_name: str,
    synonyms_list: list,
    fgm_token: str,
    candidate_count: int,
    min_name_length: int,
    max_name_length: int,
    name_cutoff_length: int,
    time_out: int = 2,
):
    """

    Pamameters
    ----------
    store_name: str
        The store name input user provide in the API
    synonyms_list: list
        The synonyms words list for input store name
    fgm_token: str
        The token generated when user logs in
    candidate_count: int
        The amount of suggested store names
    min_name_length: int
        The min length of each suggested store name
    max_name_length: int
        The max length of each suggested store name
    name_cutoff_length: int
        When the initial store name is too long, how many chars we need to keep
    time_out: int
        The amount of second to time out

    Return
    ------
    suggested_name: list
        Suggested store names

    """
    assert isinstance(synonyms_list, list), "synonyms_list must be list"
    assert isinstance(candidate_count, int), "candidate_count must be int"
    assert isinstance(fgm_token, str), "token must be str"
    assert isinstance(min_name_length, int), "min_name_length must be int"
    assert isinstance(max_name_length, int), "max_name_length must be int"
    assert (
        min_name_length <= max_name_length
    ), "min_name_length must be smaller or equal to max_name_length"
    assert isinstance(name_cutoff_length, int), "name_cutoff_length must be int"
    assert (
        min_name_length <= name_cutoff_length <= max_name_length
    ), "name_cutoff_length must <= max_name_length and >= min_name_length"
    assert isinstance(time_out, int), "time_out must be int"

    suggested_names_with_score = {}
    # Get the product of similarity scores of all words in each combo, and sort the
    # list based on the product
    filtered_synonyms_list = profanity_screen_word(synonyms_list, fgm_token)
    for word_combo in product(*filtered_synonyms_list):
        suggested_name = " ".join(word_combo)
        score = 1
        for i in range(len(word_combo)):
            score *= filtered_synonyms_list[i][word_combo[i]]
        suggested_names_with_score[suggested_name] = score
    suggested_names = [
        k
        for k, v in sorted(
            suggested_names_with_score.items(), key=lambda item: item[1], reverse=True
        )
    ]
    suggested_names = _filter_existing_names(suggested_names, fgm_token)

    # Filter out short and long names
    suggested_names = _filter_store_name_length(
        suggested_names,
        min_name_length=min_name_length,
        max_name_length=max_name_length,
    )

    start_time = time.time()
    # init store_names_client offset
    store_names_client.init()

    while len(suggested_names) < candidate_count:
        # store_names_client loads some store_names before api call, add loaded store_names to suggested_names
        # read 2*candidate_count of results from database results, in case there are not enough results after filtering
        popular_words = store_names_client.add_store_names(candidate_count)

        # Break the loop when popular_words is empty which means we have iterated
        # all popular words in our db
        if not popular_words:
            break

        extra_suggested_names = []

        # If the suggested names list is not empty append the popular words to the already suggested names
        if suggested_names:
            for name in suggested_names:
                for word in popular_words:
                    # Append the popular word only if it doesn't exist in the current suggested name
                    if word.lower() not in name.lower():
                        suggested_name = name + " " + word
                        extra_suggested_names.append(suggested_name)

        # Else if suggested names list is empty,
        # then use the store name input given by user to append the popular words.
        else:
            # If the store name is sensitive, set it as empty str
            if not profanity_screen_word([{store_name: 1}], fgm_token)[0]:
                store_name = ""

            # Only get the name_cutoff_length chars if the store name is too long
            if len(store_name) > name_cutoff_length:
                if " " not in store_name:
                    store_name = store_name[:name_cutoff_length]
                else:
                    store_name = store_name[
                        : store_name[: name_cutoff_length + 1].rindex(" ")
                    ]

            for word in popular_words:
                # Append the popular word only if it doesn't exist in the user input name
                if word.lower() not in store_name.lower():
                    suggested_name = store_name + " " + word
                    extra_suggested_names.append(suggested_name.strip())

        # Check for existing names and removing them
        filtered_extra_names = _filter_existing_names(extra_suggested_names, fgm_token)

        # Extending the previously suggested names to the new suggested names
        suggested_names.extend(filtered_extra_names)

        if time.time() - start_time > time_out:
            break

    return suggested_names[:candidate_count]


def _filter_store_name_length(
    suggested_names: list, min_name_length: int, max_name_length: int
):
    filtered_suggested_names = []
    for name in suggested_names:
        if min_name_length <= len(name) <= max_name_length:
            filtered_suggested_names.append(name)
    return filtered_suggested_names
