"""
The text module provides functions to preprocess text data for feature engineer.
"""
import string

import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer
from nltk.stem import PorterStemmer
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer

from app.main.util._processor import _Processor


class TextClean(_Processor):
    """
    This class provide the methods to clean text data
    """

    def __init__(
        self,
        text_cols: list,
        fill_na: bool = True,
        fill: str = "",
        to_lower: bool = True,
        remove_numbers: bool = True,
        remove_punc: bool = True,
        remove_whitespace: bool = True,
        tokenization: bool = True,
        remove_stopwords: bool = True,
        stop_words: list = None,
        stemming: bool = True,
        stemmer_type: str = "porter",
        lemmatization: bool = False,
        rejoin: bool = False,
    ):
        """Initialize parameters

        Parameters
        ----------
        text_cols: list
            a list of columns names indicating text columns
        fill_na: boolean, default=True
            a binary parameter indicating to fill na or not
        fill: str, default=""
            a str parameter to fill na
        to_lower: boolean, default=True
            a binary parameter indicating to convert text to lowercase or not
        remove_numbers: boolean, default=True
            a binary parameter indicating to remove numbers or not
        remove_punc: boolean, default=True
            a binary parameter indicating to remove punctuation or not
        remove_whitespace: boolean, default=True
            a binary parameter indicating to remove whitespace or not
        tokenization: boolean, default=True
            a binary parameter indicating to tokenize or not
        remove_stopwords: boolean, default=True
            a binary parameter indicating to remove stopwords or not
        stop_words: list, default=None
            a list of stopwords
        stemming: boolean, default=True
            a binary parameter indicating to do stemming or not
        stemmer_type: str, default="porter"
            a str parameter indicating which stemmer to use
            options are "porter", "snowball", and "lancaster"
        lemmatization: boolean, default=False
            a binary parameter indicating to do lemmatization or not
        rejoin: boolean, default=False
            a binary parameter indicating rejoin tokens to sentences or not
        Example
        -------
        >>> import pandas as pd
        >>> from app.main.util._text_clean import TextClean
        >>> data = pd.DataFrame(["This is a sample sentence",],
        ...                     columns=["text"],)
        >>> TextClean(text_cols=["text"]).transform(data)
                       text
        0  [sampl, sentenc]
        """
        super().__init__()
        # globalize the variables
        for name in self.param_names:
            setattr(self, name, locals()[name])

        self._type_checking()

    def transform(self, data: pd.DataFrame):
        """Transform function to apply text cleaning methods on given data

        Parameters
        ----------
        data: pd.DataFrame
            The data that need to be processed

        Returns
        -------
        result: pd.Dataframe
            A dataframe cleaned text_cols.
            Same shape as input data frame.

        """
        super().transform(data)
        df = data[self.text_cols]
        # fill na
        if self.fill_na:
            df = df.fillna(self.fill)

        # to lowercase
        if self.to_lower:
            for column in df.columns:
                df[column] = df[column].str.lower()

        # remove numbers
        if self.remove_numbers:
            for column in df.columns:
                df[column] = df[column].astype(str).str.replace(r"\d+", "")

        # remove punctuation
        if self.remove_punc:
            for column in df.columns:
                df[column] = df[column].str.replace(
                    "[{}]".format(string.punctuation), ""
                )

        # remove whitespaces
        if self.remove_whitespace:
            for column in df.columns:
                df[column] = df[column].str.strip()

        # tokenization
        if self.tokenization:
            # if there is Null in data, report error
            assert (
                not df.isnull().values.any()
            ), "Null must be filled to do tokenization"

            for column in df.columns:
                df[column] = df[column].apply(word_tokenize)

        # remove stop words
        if self.remove_stopwords:
            # if not tokenized, report error
            self.__check_tokenization(self.tokenization, "remove stopwords")
            # assign nltk stopwords if stop_words is None
            if not self.stop_words:
                self.stop_words = set(stopwords.words("english"))
            else:
                assert isinstance(
                    self.stop_words, (list, set)
                ), "stop_words must be a list of words"

            for column in df.columns:
                df[column] = df[column].apply(
                    lambda tokens: [
                        token for token in tokens if token not in self.stop_words
                    ]
                )

        # stemming
        if self.stemming:
            # if not tokenized, report error
            self.__check_tokenization(self.tokenization, "do stemming")

            # define stemmer
            if self.stemmer_type == "porter":
                stemmer = PorterStemmer()
            elif self.stemmer_type == "snowball":
                stemmer = SnowballStemmer("english")
            else:
                stemmer = LancasterStemmer()

            for column in df.columns:
                df[column] = df[column].apply(
                    lambda tokens: [stemmer.stem(token) for token in tokens]
                )

        # lemmatization
        if self.lemmatization:
            # if not tokenized, report error
            self.__check_tokenization(self.tokenization, "do lemmatization")

            lemmatizer = WordNetLemmatizer()
            for column in df.columns:
                df[column] = df[column].apply(
                    lambda tokens: [lemmatizer.lemmatize(token) for token in tokens]
                )

        # rejoin
        if self.rejoin:
            # if not tokenized, report error
            self.__check_tokenization(self.tokenization, "rejoin")

            for column in df.columns:
                df[column] = df[column].str.join(" ")

        result = data.copy()
        result[self.text_cols] = df[self.text_cols]

        return result

    def _type_checking(self):
        super()._type_checking()
        assert isinstance(self.text_cols, list), "text_cols must be a list of columns"
        assert isinstance(self.fill_na, bool), "fill_na only accept True or False"
        assert isinstance(self.fill, str), "Filling object must be a string"
        assert isinstance(self.to_lower, bool), "to_lower only accept True or False"
        assert isinstance(
            self.remove_numbers, bool
        ), "remove_numbers only accept True or False"
        assert isinstance(
            self.remove_punc, bool
        ), "remove_punc only accept True or False"
        assert isinstance(
            self.remove_whitespace, bool
        ), "remove_whitespace only accept True or False"
        assert isinstance(
            self.tokenization, bool
        ), "tokenization only accept True or False"
        assert isinstance(
            self.remove_stopwords, bool
        ), "remove_stopwords only accept True or False"
        assert isinstance(self.stemming, bool), "stemming only accept True or False"
        assert (
            self.stemmer_type == "porter" or "snowball" or "lancaster"
        ), "stemmer could be porter or snowball or lancaster"
        assert isinstance(
            self.lemmatization, bool
        ), "lemmatization only accept True or False"
        assert isinstance(self.rejoin, bool), "rejoin only accept True or False"

    def __check_tokenization(self, tokenization, action):
        """A helper function to checkout tokenization"""
        assert isinstance(action, str), "action object must be a string"
        assert tokenization, "Data must be tokenized to " + action


class TextCombine(_Processor):
    """
    This class provide the methods to combine text data
    """

    def __init__(
        self,
        input_cols: list,
        output_col: str,
        remove_input_cols: bool = True,
        output_str: bool = True,
    ):
        """Initialize parameters

        Parameters
        ----------
        input_cols: list
            required columns to do combination
        output_col: str
            User need to define the name of output combined column
        remove_input_cols: bool, default = True
            Remove input columns when True is given
        output_str: bool, default = True
            join output column as a string when True is given
        Example
        -------
        >>> from app.main.util._text_clean import TextCombine
        >>> data = pd.DataFrame([["item1",["text1"],["text2"]],
        ...                     ["item2",["text3"],["text4"]]],
        ...                     columns=["Item", "A", "B"])
        >>> TextCombine(input_cols=["A", "B"],
        ...             output_col="Combined",
        ...         ).transform(data)
            Item     Combined
        0  item1  text1 text2
        1  item2  text3 text4
        """
        super().__init__()
        # globalize the variables
        for name in self.param_names:
            setattr(self, name, locals()[name])

        self._type_checking()

    def transform(self, data: pd.DataFrame):
        """Transform function to apply text combine methods
        on given data

        Parameters
        ----------
        data: pd.DataFrame
            The data that need to be processed

        Returns
        -------
        result: pd.Dataframe
            A dataframe combined text_cols.
        """
        super().transform(data)
        item_data = data.copy()

        # initial output columns with empty lists
        item_data[self.output_col] = ""
        item_data[self.output_col] = item_data[self.output_col].apply(list)

        # merge input columns
        for col in self.input_cols:
            assert (
                item_data.applymap(type).astype(str)[col].astype(str)[0]
                == "<class 'list'>"
            ), "Input column data should be a list type"
            item_data[self.output_col] += item_data[col]

        # join out put column as a list
        if self.output_str:
            item_data[self.output_col] = item_data[self.output_col].apply(" ".join)

        # remove input columns
        if self.remove_input_cols:
            item_data = item_data.drop(self.input_cols, axis=1)

        return item_data

    def _type_checking(self):
        super()._type_checking()
        assert isinstance(
            self.input_cols, list
        ), "require_cols must be a list of columns"
        assert isinstance(self.output_col, str), "output_col object must be a string"
