"""
This module is to use word embedding api to transform
text data into vectors with specific dimensions
Inherited from WordEmbedding class
"""
import json

import numpy as np
import pandas as pd
import requests

from app.main.recommender.features._word_embedding import WordEmbedding
from app.main.recommender.features._processor import _Processor


class WordEmbeddingApi(WordEmbedding):
    def __init__(
        self, method_type: str, input_col: str, api_url: str, vector_length: int = 300
    ):
        """
        Initialize parameters
        Parameters
        ----------
        method_type: str
            Choose method_type from "average" and "tfidf"
        input_col: str
            Input column of given dataframe
        api_url: str
            Given API URL to get word embedding vectors
        vector_length: int, default=300
            The vector length of given word embedding vectors
        Examples
        -------
        >>> import pandas as pd
        >>> from app.main.recommender.features._word_embedding_api import WordEmbeddingApi
        >>> text_data = pd.DataFrame([["1", "how you"],["2", "how are you"]],
        ... columns=["Item", "Combined"]).set_index("Item")
        >>> word_embedding_api = WordEmbeddingApi("average", "Combined",
        ... "https://mik.dev.platform.michaels.com/api/rec/word_embedding/word_vectors?words=", 300)
        >>> result = word_embedding_api.transform(text_data, "matrix")
        >>> result.todense()
        """
        # globalize the variables
        _Processor.__init__(self)
        for name in self.param_names:
            setattr(self, name, locals()[name])
        self.tfidf = None
        self._type_checking()

    def transform(self, data: pd.DataFrame, return_format: str = "matrix"):
        return super().transform(data, return_format)

    def _get_vector(self, text: str, feature_names: list = None):
        """
        Override from _get_vector() function in WordEmbedding class
        so that we can use api_url instead of pretrained model path
        Parameters
        ----------
        text: str
            The text in input column of the dataframe
        feature_names: list, default = None
            A list of all word features after using tfidf vectorizer
        Return
        -------
        arr: numpy.ndarray
            The vector of the text data
        """
        arr = np.zeros(self.vector_length)
        if not text:
            return arr
        if not isinstance(text, str):
            raise TypeError("The data type of text in input column should be string")
        try:
            data = requests.get(self.api_url + text)
            model_data = json.loads(data.content)
        except Exception:
            raise ValueError("The API URL is incorrect")
        words = str(text).split(" ")
        if self.method_type == "average":
            for word in words:
                if len(model_data[word]) != 0:
                    if len(model_data[word]) != self.vector_length:
                        raise ValueError("vector length is incorrect")
                    vec = np.array(model_data[word])
                    arr = arr + vec
        elif self.method_type == "tfidf":
            # get tfidf score of each word in the text string
            tfidf_scores = super()._get_tfidf_for_words(text, feature_names)
            for word in words:
                if len(model_data[word]) != 0 and word in tfidf_scores:
                    if len(model_data[word]) != self.vector_length:
                        raise ValueError("vector length is incorrect")
                    vec = np.array(model_data[word]) * tfidf_scores.get(word)
                    arr = arr + vec
        return arr / len(words)

    def _type_checking(self):
        assert isinstance(self.api_url, str), "api_url must in string type"
        assert isinstance(self.vector_length, int), "vector_length must be int type"
        assert isinstance(self.input_col, str), "input_col must in string type"
        assert self.method_type in [
            "average",
            "tfidf",
        ], "method_type should be average or tfidf"
