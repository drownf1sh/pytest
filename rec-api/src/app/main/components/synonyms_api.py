from mongoengine import DoesNotExist
from app.main.util.global_vars import suggested_store_name_count
from app.main.model.synonyms import SynonymsWords


def process_non_human_names(words: list):
    """
    Main function. Get a list of words, and return the lists of synonyms with similarity scores.
    :param words:list
    :return: list
    """
    assert isinstance(words, list), "words must be list"
    synonyms_words_list = []
    for word in words:
        try:
            score_dict = SynonymsWords.objects(search_word=word).get().synonyms_dict
        except DoesNotExist:
            score_dict = {word: 1}
        synonyms_words_list.append(get_top_k(score_dict))
    return synonyms_words_list


def get_top_k(score_dict: dict):
    """
    Get TopK similarity scores
    :param score_dict:dict
    :return: dict
    """
    results = {}
    for k, v in sorted(score_dict.items(), key=lambda item: item[1], reverse=True)[
        :suggested_store_name_count
    ]:
        results[k.title()] = v
    return results
