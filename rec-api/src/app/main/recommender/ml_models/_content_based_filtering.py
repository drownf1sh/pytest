"""
This module provides a content-based filtering class to calculate
the similarities between each pair of items and provide the
k most similar items as recommendations.
"""
import pandas as pd

from app.main.recommender.ml_models._RecommendationModel import _RecommendationModel
from app.main.recommender.ml_models._similarity import similarity
from app.main.recommender.features._cluster_labeler import KMeansLabeler


class ContentBasedFiltering(_RecommendationModel):
    """
    Class that provides the content-based filtering model.
    """

    def __init__(
        self,
        method_name: str = "cosine",
        output_item_col: str = "item_id",
    ):
        """
        Initialize parameters

        Parameters
        ----------
        method_name: str, default = 'cosine'
            The method intends to calculate similarity, default to cosine.
            Support cosine, pearson, and jaccard.
        output_item_col: str, default = "item_id"
            a column name in result to identify items

        Example
        -------
        >>> import pandas as pd
        >>> from src.app.main.recommender.ml_models._content_based_filtering import ContentBasedFiltering
        >>> df  = pd.DataFrame([
        ...     [1, 0, 1, 1, 0],
        ...     [1, 0, 0, 1, 1],
        ...     [1, 0, 1, 0, 0],
        ...     [0, 1, 0, 1, 1],
        ...     [1, 1, 1, 0, 1]
        ... ],
        ...     columns = ["f1", "f2", "f3", "f4", "f5"],
        ...     index = ["Item1", "Item2", "Item3", "Item4", "Item5"],)
        >>> label_df = pd.DataFrame([[1], [1], [1], [2], [2]],
        ...     columns = ["label"],
        ...     index = ["Item1", "Item2", "Item3", "Item4", "Item5"],)
        >>> model = ContentBasedFiltering()
        >>> model = model.fit(df)
        >>> model.predict(candidate_count=3)
        [{'item_id': 'Item1', 'recommendations': ['Item3', 'Item2', 'Item5']}]
        """

        # globalize the variables
        self.method_name = method_name
        self.output_item_col = output_item_col

        # init
        super().__init__()

        # pre-define the necessary variables
        self.feature_df = None

        # check parameters type
        self._type_checking()

    def fit(self, data: pd.DataFrame):
        """
        This method fits the model with the given data.

        Parameters
        ----------
        data: pd.DataFrame
            The input dataframe for calculating similarity.
            The index should be item id.
        """
        # parameter assertion
        assert isinstance(data, pd.DataFrame), "data only accept pd.DataFrame"

        # globalize the variables
        self.feature_df = data.copy(deep=True)
        return self

    def predict(
        self,
        data: pd.DataFrame = None,
        candidate_count: int = 5,
        provide_score: bool = False,
        output_format: str = "json",
        rec_col: str = "recommendations",
        score_col: str = "score",
    ):
        """
        This method gets a final recommendation list based on the result from the model.

        Parameters
        ----------
        data: pd.DataFrame, default = None
            The input dataframe for calculating similarity.
            The index should be item id.
        candidate_count: int, default = 5
            Define how many similar items
        provide_score: bool, default = False
            output item score when condition is True
        output_format: str, default = 'json'
            Provide the format of output, can be 'dataframe', 'json'.
        rec_col: str, default = "recommendations"
            a column name in the result to provide recommendations
        score_col: str, default = "score"
            a column name in the result to provide scores

        Returns
        -------
        result: list or pd.DataFrame
            Provide top similar items in same cluster and
            different clusters
        """

        # type check for predict function
        super().predict(
            candidate_count=candidate_count,
            output_format=output_format,
            provide_score=provide_score,
            rec_col=rec_col,
            score_col=score_col,
        )
        if data is not None:
            assert isinstance(data, pd.DataFrame), "data only accept pd.DataFrame"

        # Calculate similarity for each item
        if data is None:
            similarity_df = similarity(
                self.feature_df,
                method_name=self.method_name,
                columns=list(self.feature_df.index),
                index=list(self.feature_df.index),
            )
        else:
            assert isinstance(data, pd.DataFrame), "data only accept pd.DataFrame"
            similarity_df = similarity(
                data,
                self.feature_df,
                method_name=self.method_name,
                columns=list(self.feature_df.index),
                index=list(data.index),
            ).T

        # Get top k similar items
        result = self._k_top_similar_items(
            similarity_df,
            candidate_count,
            self.output_item_col,
            rec_col,
            score_col,
            provide_score,
            output_format,
        )

        return result

    def _k_top_similar_items(
        self,
        similarity_df: pd.DataFrame,
        candidate_count: int,
        item_col: str = "item_id",
        rec_col: str = "recommendations",
        score_col: str = "score",
        provide_score: bool = False,
        output_format: str = "json",
    ):
        """
        Helper function to generate top k similar items
        """

        # develop a helper function to predict for a single item
        def _predict_for_one_item(item):
            # convert str to list to extract pd.DataFrame object
            item = [item]

            # filter the target item
            target_item_df = similarity_df[item]
            # remove target item
            target_item_df = target_item_df[target_item_df.index != item[0]]

            # get top k recommendations
            result = target_item_df.sort_values(item, ascending=False)[:candidate_count]

            # convert result to df
            if not provide_score:
                result = pd.DataFrame(
                    zip(
                        [item[0]],
                        [list(result.index)],
                    ),
                    columns=[item_col, rec_col],
                )

            # add similarity scores
            else:
                result = pd.DataFrame(
                    zip(
                        [item[0]],
                        [list(result.index)],
                        [result[item[0]].to_list()],
                    ),
                    columns=[
                        item_col,
                        rec_col,
                        score_col,
                    ],
                )
            return result

        result = pd.DataFrame()
        for item in similarity_df.columns:
            result = pd.concat([result, _predict_for_one_item(item)], axis=0)
            result.reset_index(drop=True, inplace=True)

        # change output format
        result = self._format_transform(result, output_format)

        return result

    def _type_checking(self):
        """
        This method checks the types of the inputs for model initialization.
        """
        assert self.method_name in [
            "cosine",
            "pearson",
            "jaccard",
        ], "method_name must be 'cosine' or 'pearson' or 'jaccard'"
        assert isinstance(self.output_item_col, str), "item_col must be str"


class StreamingContentBasedFiltering(_RecommendationModel):
    """
    Class that provides the streaming content-based filtering model.
    """

    def __init__(
        self,
        labeler,
        method_name: str = "cosine",
        cluster_num: int = 2,
        output_item_col: str = "item_id",
    ):
        """Initialize parameters

        Parameters
        ----------
        labeler
            Input a clustering model for data segmentation.
        method_name: str, default = 'cosine'
            The method intends to calculate similarity, default to cosine.
            Support cosine, pearson, and jaccard.
        cluster_num: int, default = 2
            The num of labeled clusters will be used to get recommendations
        output_item_col: str, default = "item_id"
            a column name in result to identify items

        Example
        -------
        >>> import pandas as pd
        >>> from src.app.main.recommender.features._cluster_labeler import KMeansLabeler
        >>> from src.app.main.recommender.ml_models._content_based_filtering import StreamingContentBasedFiltering
        >>> df  = pd.DataFrame([
        ...     [1, 0, 1, 1, 0],
        ...     [1, 0, 0, 1, 1],
        ...     [1, 0, 1, 0, 0],
        ...     [0, 1, 0, 1, 1],
        ...     [1, 1, 1, 0, 1]
        ... ],
        ...     columns = ["f1", "f2", "f3", "f4", "f5"],
        ...     index = ["Item1", "Item2", "Item3", "Item4", "Item5"],)
        >>> labeler = KMeansLabeler(random_state=0)
        >>> model = StreamingContentBasedFiltering(labeler, cluster_num=2)
        >>> model.fit(df)
        >>> model.predict(df[:1],candidate_count=3)
        [{'item_id': 'Item1', 'recommendations': ['Item3', 'Item5']}]
        """

        # init
        super().__init__()

        # globalize the variables
        for name in self.param_names:
            setattr(self, name, locals()[name])

        # pre-define the necessary variables
        self.nearby_cluster_df = None

        # check the types of the inputs
        self._type_checking()

    def fit(self, data: pd.DataFrame):
        """
        This method fits the model with the given data.

        Parameters
        ----------
        data: pd.DataFrame
            The input dataframe for calculating similarity.
            The index should be item id.
        """
        # parameter assertion
        assert isinstance(data, pd.DataFrame), "data only accept pd.DataFrame"

        # globalize the variables
        self.feature_df = data.copy(deep=True)
        feature_df_label = self.labeler.fit_transform(self.feature_df)
        feature_df_label.index = self.feature_df.index
        self.feature_df["cluster"] = feature_df_label
        self.feature_df["item_id"] = self.feature_df.index

        # get all cluster centers and similarity between different clusters
        centers = pd.DataFrame(self.labeler.kmeans.cluster_centers_)
        cluster_labels = similarity(
            centers,
        )

        # get cluster_num nearby clusters for each cluster
        cluster_labels["cluster"] = cluster_labels.index
        self.nearby_cluster_df = (
            pd.melt(
                cluster_labels,
                id_vars="cluster",
                var_name="nearby_cluster",
                value_name="score",
            )
            .groupby("cluster")
            .apply(lambda x: x.nlargest(self.cluster_num, ["score"]))
            .reset_index(drop=True)[["cluster", "nearby_cluster"]]
        )

    def predict(
        self,
        data: pd.DataFrame,
        candidate_count: int = 5,
        provide_score: bool = False,
        output_format: str = "json",
        rec_col: str = "recommendations",
        score_col: str = "score",
    ):
        """
        This method gets a final recommendation list based on the result from the model.

        Parameters
        ----------
        data: pd.DataFrame
            The input dataframe for calculating similarity.
            The index should be item id.
            The data should only include one item.
        candidate_count: int, default = 5
            Define how many similar items
        provide_score: bool, default = False
            output item score when condition is True
        output_format: str, default = 'json'
            Provide the format of output, can be 'dataframe', 'json'.
        rec_col: str, default = "recommendations"
            a column name in the result to provide recommendations
        score_col: str, default = "score"
            a column name in the result to provide scores

        Returns
        -------
        result: list or pd.DataFrame
            Provide top similar items in same cluster and
            different clusters
        """

        # type check for predict function
        super().predict(
            candidate_count=candidate_count,
            output_format=output_format,
            provide_score=provide_score,
            rec_col=rec_col,
            score_col=score_col,
        )
        assert isinstance(data, pd.DataFrame), "data only accept pd.DataFrame"

        # copy data to input_data
        input_data = data.copy(deep=True)

        # initialize final result
        result = pd.DataFrame()

        # clustering data
        input_data_labels = self.labeler.transform(input_data)
        input_data_labels.index = input_data.index
        input_data["cluster"] = input_data_labels

        # group by nearby cluster and cluster separately
        input_data_cluster_dicts = dict(tuple(input_data.groupby("cluster")))

        # iterate by input_data's clusters
        for predict_cluster in input_data_cluster_dicts:
            # get the input_data in same cluster
            predict_cluster_data = input_data_cluster_dicts[predict_cluster]

            # get the nearby clusters' item data
            cluster_data = self.feature_df[
                self.feature_df["cluster"].isin(
                    self.nearby_cluster_df[
                        self.nearby_cluster_df["cluster"] == predict_cluster
                    ]["nearby_cluster"]
                )
            ]

            # drop cluster and item_id columns before calculating similarity
            predict_cluster_data.drop(columns=["cluster"], inplace=True)
            cluster_data.drop(columns=["cluster", "item_id"], inplace=True)

            # calculate similarity between input_data and nearby clusters' items data
            similarity_df = similarity(
                predict_cluster_data,
                cluster_data,
                method_name=self.method_name,
                columns=list(cluster_data.index),
                index=list(predict_cluster_data.index),
            )

            # set the index/item_id to be column so can melt dataframe later
            similarity_df[self.output_item_col] = similarity_df.index

            # get the recommendation result for one cluster in input_data
            one_cluster_result = pd.melt(
                similarity_df,
                id_vars=self.output_item_col,
                var_name=rec_col,
                value_name=score_col,
            )

            # groupby item_id and sort recommendations except the item itself
            one_cluster_result = (
                one_cluster_result[
                    one_cluster_result[self.output_item_col]
                    != one_cluster_result[rec_col]
                ]
                .groupby(self.output_item_col)
                .apply(lambda x: x.nlargest(candidate_count, ["score"]))
                .reset_index(drop=True)
            )

            one_cluster_result = pd.DataFrame(
                one_cluster_result.groupby(self.output_item_col).agg(list)
            ).reset_index()

            # add item result to final result
            result = pd.concat([result, one_cluster_result], axis=0)

        if not provide_score:
            result = result[[self.output_item_col, rec_col]]

        # change output format
        result = self._format_transform(result, output_format)

        return result

    def _type_checking(self):
        assert self.method_name in [
            "cosine",
            "pearson",
            "jaccard",
        ], "method_name must be 'cosine' or 'pearson' or 'jaccard'"
        assert isinstance(self.output_item_col, str), "item_col must be str"
        assert isinstance(self.cluster_num, int), "cluster_num must be int"
