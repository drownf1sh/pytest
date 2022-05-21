"""
This module provides clustering labelers to group items into
different clusters.
"""
from typing import Union

import pandas as pd
import scipy
from sklearn.cluster import KMeans

from app.main.recommender.features._transformer import _Transformer


class KMeansLabeler(_Transformer):
    """
    This module provides clustering labelers to group items into
    different clusters.
    """

    def __init__(
        self,
        n_clusters: int = 2,
        index: list = None,
        random_state: int = None,
        label_col: str = "label",
    ):
        """Use test features to train a kmeans clustering model to
        classify items into multiple groups

        Parameters
        ----------
        n_clusters: int, default = 2
            The number of clusters
        index: list, default = None
            The index of item table, should be a list of item names
        random_state: int, default = None
            The random seed
        label_col: str, default = "label"
            The label table column

        Returns
        -------
        label_df: pd.DataFrame of (n_samples, 1)
            The label dataframe contains clustering results

        Example
        -------
        >>> import scipy
        >>> from app.main.recommender.features._cluster_labeler import KMeansLabeler
        >>> feature_array = [[0.        ,0.        ,0.        ,0.        ,0.49084524,
        ...                   0.        ,0.87124678,0.        ,0.        ],
        ...                   [0.        ,0.        ,0.        ,0.        ,0.49084524,
        ...                   0.        ,0.        ,0.87124678,0.        ],
        ...                   [0.        ,0.        ,0.        ,0.8198869 ,0.57252551,
        ...                   0.        ,0.        ,0.        ,0.        ],
        ...                   [0.        ,0.52335825,0.52335825,0.42224214,0.        ,
        ...                   0.        ,0.        ,0.        ,0.52335825],
        ...                   [0.65690037,0.        ,0.        ,0.        ,0.37008621,
        ...                   0.65690037,0.        ,0.        ,0.        ]]
        >>> feature_matrix = scipy.sparse.csr_matrix(feature_array)
        >>> index = ['item1', 'item2', 'item3', 'item4', 'item5']
        >>> cluster_labeler = KMeansLabeler(index = index, random_state=0)
        >>> label_df = cluster_labeler.fit_transform(feature_matrix)
        >>> print(label_df)
                label
        item1      1
        item2      1
        item3      0
        item4      0
        item5      1
        """
        super().__init__()
        # globalize the variables
        for name in self.param_names:
            setattr(self, name, locals()[name])
        self.kmeans = None
        self._type_checking()

    def fit(self, feature_matrix: Union[pd.DataFrame, scipy.sparse.csr_matrix]):
        """
        This method fits the model with the given data to generate clustering labelers.

        Parameters
        ----------
        feature_matrix: pd.DataFrame or scipy.sparse.csr_matrix
            The feature matrix will be used to train the model
        """
        self._data_type_checking(feature_matrix)
        # Train kmeans clustering model
        self.kmeans = KMeans(
            n_clusters=self.n_clusters, random_state=self.random_state
        ).fit(feature_matrix)
        return self

    def transform(self, feature_matrix: Union[pd.DataFrame, scipy.sparse.csr_matrix]):
        """
        This method will group items into different clusters..

        Parameters
        ----------
        feature_matrix: pd.DataFrame or scipy.sparse.csr_matrix
            The feature matrix will be used to train the model

        Returns
        -------
        label_df: pd.DataFrame of (n_samples, 1)
            The label dataframe contains clustering results
        """
        self._data_type_checking(feature_matrix)

        # convert labels to a dataframe
        label_df = pd.DataFrame(
            self.kmeans.predict(feature_matrix), columns=[self.label_col]
        )

        # Assign index to label df
        if self.index is not None:
            label_df.index = self.index

        return label_df

    def fit_transform(
        self, feature_matrix: Union[pd.DataFrame, scipy.sparse.csr_matrix]
    ):
        return super().fit_transform(feature_matrix)

    def _data_type_checking(self, data: Union[pd.DataFrame, scipy.sparse.csr_matrix]):
        assert isinstance(
            data, (pd.DataFrame, scipy.sparse.csr_matrix)
        ), "data must be pd.DataFrame or scipy.sparse.csr_matrix"

    def _type_checking(self):
        super()._type_checking()
        assert (
            isinstance(self.n_clusters, int) and self.n_clusters > 0
        ), "n_clusters must be positive int type"
        if self.index is not None:
            assert isinstance(list(self.index), list), "index must be array like"
        if self.random_state is not None:
            assert isinstance(
                self.random_state, int
            ), "random_state must be positive int type"
        assert isinstance(self.label_col, str), "n_clusters must be string type"
