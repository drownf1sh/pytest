"""
This module is to use word embedding models to transform
text data into vectors with specific dimensions
"""
import numpy as np
import pandas as pd
import scipy
from sklearn.feature_extraction.text import TfidfVectorizer

from app.main.recommender.features._processor import _Processor


class WordEmbedding(_Processor):
    """
    This class provide methods to use word embedding model to get text vectors.
    """

    def __init__(self, model_path: str, input_col: str, method_type: str = "average"):
        """
        initialize parameters

        Parameters
        ----------
        model_path: str
            The local file path of pretrained model
            (Word2Vec, GloVe and Fasttext etc.).
            The pretrained model should be able to read in unicode format.
            Please check out the Confluence page for more details:
            https://michaels.atlassian.net/wiki/spaces/REC/pages/498335820/Feature+Engineering
        input_col: str
            The input column name to be transformed
        method_type: str, default = “average”
            Choose methods to calculate text vectors by using
            vectors of each word in it, default to use average calculation method
        Examples
        -------
        >>> import pandas as pd
        >>> from app.main.recommender.features._word_embedding import WordEmbedding
        >>> text_data = pd.DataFrame([["1", "how you"],["2", "how are you"]],
        ... columns=["Item", "Combined"]).set_index("Item")
        >>> word_embedding = WordEmbedding("word_embedding_model.txt", "Combined")
        >>> result = word_embedding.transform(text_data)
        >>> result.todense()
        matrix([[ 0.25      ,  0.1       ,  0.2       , -0.05      , -0.35      ],
                [ 0.06666667,  0.1       ,  0.23333333, -0.1       , -0.26666667]])
        """
        super().__init__()
        # globalize the variables
        for name in self.param_names:
            setattr(self, name, locals()[name])
        self.tfidf = None
        self._type_checking()

        # load model
        self.vector_length = None
        try:
            file = open(model_path, "r", encoding="utf-8", newline="\n")
            data = dict()
            for line in file:
                tokens = line.rstrip().split(" ")
                word = tokens[0]
                vectors = np.asarray(tokens[1:])
                if self.vector_length is None:
                    self.vector_length = vectors.shape[0]
                data[word] = vectors
            self.model = data
        except FileNotFoundError:
            print("File not found")
        except UnicodeDecodeError:
            print("This model type is not supported")

    def transform(self, data: pd.DataFrame, return_format: str = "matrix"):
        """
        This function transforms text data into vectors using word embedding
        model. Different calculation methods can be used to get text vectors:
        Use average calculation method if input method_type is "average".
        Use average tfidf calculation if input method_type is "tfidf".

        Parameters
        ----------
        data: pandas.DataFrame
            The input dataframe containing input column data to be transformed
        return_format: str, default = "matrix"
            One of "dataframe", "matrix", or "array". Defaults to "matrix"

        Return
        -------
        vector_array: scipy.sparse.csr_matrix
            A matrix shape of (input data length, model vector length)
        """
        super().transform(data)

        assert self.input_col in data.columns, "Input column is required in dataframe"
        assert return_format in ["dataframe", "matrix", "array"], (
            "return_format must be one of matrix, array, " "or dataframe "
        )
        if self.method_type == "average":
            vector_array = data[self.input_col].apply(lambda x: self._get_vector(x))
        else:
            self.tfidf = TfidfVectorizer()
            self.tfidf.fit(data[self.input_col])
            feature_names = self.tfidf.get_feature_names()
            vector_array = data[self.input_col].apply(
                lambda x: self._get_vector(x, feature_names)
            )

        if return_format == "matrix":
            # convert data to sparse matrix
            try:
                return scipy.sparse.csr_matrix(np.vstack(vector_array))
            except ValueError:
                print(
                    "Unknown word detected. Please try array or dataframe as "
                    "return_format to avoid concatenation error"
                )
        elif return_format == "array":
            # return data as array
            return vector_array
        elif return_format == "dataframe":
            # return data as pandas.dataframe
            return pd.DataFrame(vector_array)

    def _get_vector(self, text: str, feature_names: list = None):
        """
        This is a private function to get text vector
        by calculating the vector of each word in it
        Support average method and average tfidf method
        The text data should be in string type

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
        words = str(text).split(" ")
        if self.method_type == "average":
            for word in words:
                if word in self.model:
                    vec = self.model.get(word).astype(float)
                    arr = arr + vec
        elif self.method_type == "tfidf":
            # get tfidf score of each word in the text string
            tfidf_scores = self._get_tfidf_for_words(text, feature_names)
            for word in words:
                if word in self.model and word in tfidf_scores:
                    vec = self.model.get(word).astype(float) * tfidf_scores.get(word)
                    arr = arr + vec
        return arr / len(words)

    def _get_tfidf_for_words(self, text: str, feature_names: list):
        """
        This function is used to get tfidf scores for a text string data

        Parameters
        ----------
        text: str
            Input text string data
        feature_names: list
            A list of all word features after using tfidf vectorizer

        Returns
        -------
        tfidf_scores: dict
            A dictionary of tfidf scores for input text data
        """
        if not isinstance(text, str):
            raise TypeError("The data type is not supported")
        # get tfidf matrix for given text string data
        tfidf_matrix = self.tfidf.transform([text]).todense()
        # get feature index from tfidf matrix
        feature_index = tfidf_matrix[0, :].nonzero()[1]
        # match feature names with tfidf scores for given text string data
        tfidf_scores = zip(
            [feature_names[i] for i in feature_index],
            [tfidf_matrix[0, x] for x in feature_index],
        )
        return dict(tfidf_scores)

    def _type_checking(self):
        super()._type_checking()
        assert isinstance(self.model_path, str), "model_path must in string type"
        assert isinstance(self.input_col, str), "input_col must in string type"
        assert self.method_type in [
            "average",
            "tfidf",
        ], "method_type should be average or tfidf"
