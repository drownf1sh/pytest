"""
This module provides functions to calculate similarity
between each pair of elements.
"""
from typing import Union

import numpy as np
import pandas as pd
import scipy
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import pairwise_distances


def similarity(
    data: Union[pd.DataFrame, np.ndarray, scipy.sparse.csr_matrix],
    base_data: Union[pd.DataFrame, np.ndarray, scipy.sparse.csr_matrix] = None,
    method_name: str = "cosine",
    columns: list = None,
    index: list = None,
):
    """function that calculates similarity score

    Parameters
    ----------
    data: pd.DataFrame, np.array, or scipy.sparse.csr_matrix
        The input dataframe for calculating similarity
    base_data: pd.DataFrame, np.array, or scipy.sparse.csr_matrix, default = None
        The base dataframe for calculating similarity.
        If not given, set the base_data equals to data.
    method_name: str, default = 'cosine'
        The method intends to calculate similarity, default to cosine.
        Other methods supports pearson, jaccard so far.
    columns: list, default = None,
        Specify the output matrix's column name
    index: list, default = None,
        Specify the output matrix's row(index) name

    Returns
    -------
    similarity_score: pd.Dataframe
        similarity score between each pair of elements.

    Example
    -------
    >>> from app.main.recommender.ml_models._similarity import similarity
    >>> jaccard_similarity_df = similarity(
    ...        input_matrix,
    ...        method_name="jaccard",
    ...        columns=input_columns,
    ...        index=index_columnn,
    ...        )
    >>> "Note: using jaccard similarity will convert data to boolean"
    >>>
    >>> cosine_similarity_df = similarity(input_matrix, method_name="cosine")
    >>> "Note: method_name default to cosine if not specified"
    >>>
    >>> ("method_name not in jaccard, pearson and cosine"
    ...  "will result in Invalid Method Error")
    """

    # input assertion
    def _data_type_checking(data, data_name):
        assert isinstance(data, (pd.DataFrame, np.ndarray, scipy.sparse.csr_matrix)), (
            data_name + " only accept "
            "pd.DataFrame or "
            "np.ndarray or "
            "scipy.sparse.csr_matrix"
        )

    _data_type_checking(data, "data")
    if base_data is None:
        base_data = data
    else:
        _data_type_checking(base_data, "base_data")

    method_name = method_name.lower()

    def _jaccard_pearson_array_convert(data):
        if isinstance(data, pd.DataFrame):
            return data.to_numpy()
        elif isinstance(data, scipy.sparse.csr_matrix):
            return data.toarray()
        else:
            return data

    if method_name == "jaccard":
        array = _jaccard_pearson_array_convert(data)
        base_array = _jaccard_pearson_array_convert(base_data)
        similarity_score = pd.DataFrame(
            1 - pairwise_distances(array, base_array, metric="jaccard")
        )

    elif method_name == "pearson":
        array = _jaccard_pearson_array_convert(data)
        base_array = _jaccard_pearson_array_convert(base_data)
        similarity_score = (
            pd.DataFrame(np.concatenate((array, base_array), axis=0))
            .fillna(np.nan)
            .T.corr()
            .iloc[: len(array), len(array) :]  # noqa: E203
        )

    elif method_name == "cosine":

        def _cosine_df_convert(data):
            if isinstance(data, np.ndarray):
                return pd.DataFrame(data)
            else:
                return data

        df = _cosine_df_convert(data)
        base_df = _cosine_df_convert(base_data)
        similarity_score = pd.DataFrame(cosine_similarity(df, base_df))

    else:
        assert (
            "Method name must be one of the options: jaccard, pearson and consine."
            "Default to cosine if not specified."
        )

    if columns is not None and index is not None:
        similarity_score.columns = columns
        similarity_score.index = index
    elif columns is not None or index is not None:
        assert "columns and index MUST be specified together or not specified neither"

    return similarity_score
