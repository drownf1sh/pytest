from mongoengine import DoesNotExist
import numpy as np
from app.main.model.word_embedding import WordVector, NgramWordVector, PhraseDict
from app.main.util.global_vars import word_vector_length, ngram_word_vector_length
import logging


def get_vectors_for_word_lists(**kwargs):
    """
    Get vector by specific words list
    :param words: list
        Given words list to get vector for each word
    :return: dict
        A dict holds {word:list of float values(embedding vector) for this word} pairs
    """
    words = kwargs["words"]
    result_dict = {}
    # get word vectors and combine to a JSON format then return
    words_list = words.strip().split(" ")
    for word in words_list:
        try:
            word_vector = WordVector.objects(word=word).get()
            result_dict[word] = word_vector.vector
        except DoesNotExist:
            # If not exist return an empty list
            result_dict[word] = []
    return result_dict


def get_vectors_for_ngram_word_lists(**kwargs):
    """
    Get vector by specific words list
    :param words: list
        Given words list to get vector for each ngram word
    :return: dict
        A dict holds {ngram:list of float values(embedding vector) for this ngram word} pairs
    """
    words = kwargs["words"]
    result_dict = {}
    # get word vectors and combine to a JSON format then return
    words_list = words.strip().split(" ")
    for word in words_list:
        try:
            # get ngram word vectors
            word_vector = NgramWordVector.objects(word=word).get()
            result_dict[word] = word_vector.vector
        except DoesNotExist:
            # If not exist return an empty list
            result_dict[word] = []
    return result_dict


def get_sentences_average_vectors(**kwargs):
    """
    Get average vectors for sentences
    :param sentence: str
        Given a sentence to get an average vector
    :return: dict
        A dict with 2 keys, "sentence" and "vector";
        value of "sentence" is the given sentence str;
        value of "vector" is the average list of float values(embedding vector) for all words
    """
    sentence = kwargs["sentence"]
    result_dict = {}
    arr = np.zeros(word_vector_length)
    words = sentence.split(" ")
    for word in words:
        try:
            vec = WordVector.objects(word=word).get()
            arr = arr + vec.vector
        except DoesNotExist:
            logging.warning(
                msg=f"Warning: Does not find the vector for the word: {word}"
            )
    result_dict["sentence"] = sentence
    result_dict["vector"] = (arr / len(words)).tolist()
    return result_dict


def get_sentences_average_vectors_ngram(**kwargs):
    """
    Get average vectors for sentences
    :param sentence: str
        Given a sentence to get an average vector
    :return: dict
        A dict with 2 keys, "sentence" and "vector";
        value of "sentence" is the given sentence str;
        value of "vector" is the average list of float values(embedding vector) for all ngrams
    """
    sentence = kwargs["sentence"]
    result_dict = {}
    arr = np.zeros(ngram_word_vector_length)
    words = sentence.split(" ")
    for word in words:
        try:
            vec = NgramWordVector.objects(word=word).get()
            arr = arr + vec.vector
        except DoesNotExist:
            logging.warning(
                msg=f"Warning: Does not find the vector for the word: {word}"
            )
    result_dict["sentence"] = sentence
    result_dict["vector"] = (arr / len(words)).tolist()
    return result_dict


def get_phrase_for_sentence(**kwargs):
    """
    Get ngram token list by sentence
    :param sentence: str
        Given sentnece to get ngram token list
    :return: list
        A list of ngram tokens
    """
    sentence = kwargs["sentence"].lower()
    words_list = sentence.split()
    # get ngram candidates
    def get_ngram_candid(ngram_len, words_list):
        ngram_candid = []
        for j in range(len(words_list) - ngram_len + 1):
            ngram = "_".join(words_list[j : j + ngram_len])
            ngram_candid.append(ngram)
        return ngram_candid

    bigram_candidates = get_ngram_candid(2, words_list)
    trigram_candidates = get_ngram_candid(3, words_list)
    ngrams = []
    # get trigrams in the sentence
    for trigram_candidate in trigram_candidates:
        try:
            PhraseDict.objects(ngram=trigram_candidate).get()
            ngrams.append(trigram_candidate)
        except DoesNotExist:
            logging.warning(
                msg=f"Warning: Does not find the vector for the word: {trigram_candidate}"
            )
    # get bigrams in the sentence
    for bigram_candidate in bigram_candidates:
        try:
            PhraseDict.objects(ngram=bigram_candidate).get()
            if bigram_candidate not in " ".join(ngrams):
                ngrams.append(bigram_candidate)
        except DoesNotExist:
            logging.warning(
                msg=f"Warning: Does not find the vector for the word: {bigram_candidate}"
            )
    # replace ngrams in the sentence
    for ngram in ngrams:
        ngram_in_sentence = " ".join(ngram.split("_"))
        sentence = sentence.replace(ngram_in_sentence, ngram)
    return sentence.split()
