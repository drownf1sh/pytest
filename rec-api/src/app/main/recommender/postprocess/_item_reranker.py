"""
This module provides functions to rerank recommendation lists
with the priority of certain item ids.
"""
import copy

import pandas as pd

from app.main.recommender.features._processor import _Processor


class ItemReranker(_Processor):
    """
    This class is used to prioritize item ids with a target prefix by
    a certain weight within the recommendation lists.
    """

    def __init__(
        self,
        group_col: str,
        rec_col: str,
        score_col: str,
        target_prefix: str,
        weight: float,
    ):
        """
        Initialize the parameters.

        Parameters
        ----------
        group_col: str
            Provide the name of the item column.
        rec_col: str
            Provide the name of the recommendation column.
        score_col: str
            Provide the name of the score column.
        target_prefix: str
            Provide the target prefix of items that needs prioritization.
        weight: float
            Provide the weight for prioritization.

        Example
        -------
        >>> from src.app.main.recommender.postprocess._item_reranker import ItemReranker
        >>> item_reranker = ItemReranker(
        ...    group_col="group_id", rec_col="rec", score_col="score",
        ...    target_prefix="11", weight=2.0
        ... )
        >>> item_reranker
        ItemReranker(group_col=group_id, rec_col=rec, score_col=score, \
target_prefix=11, weight=2.0)
        """
        super().__init__()
        # globalize the variables
        for name in self.param_names:
            setattr(self, name, locals()[name])

        # pre-define the necessary variables
        self.data = None

        self._type_checking()

    def transform(
        self,
        data: pd.DataFrame,
        output_format: str = "json",
        provide_score: bool = False,
        reranker_candidate_count: int = 5,
    ):
        """
        This function transforms the recommendation and score columns
        with the given rule of prioritization.

        Parameters
        ----------
        data: pd.DataFrame
            Provide the recommendation dataframe.
        output_format: str, default = 'json'
            Provide the format of output, can be 'dataframe', 'json'.
        provide_score: bool, default = False
            If True, output scores of each recommended item.
        reranker_candidate_count: int， default = 5
            Provide the number of candidates of the most popular items.

        Returns
        -------
        data: pd.DataFrame
            Provide the transformed recommendation dataframe.

        Example
        -------
        >>> from src.app.main.recommender.postprocess._item_reranker import ItemReranker
        >>> item_reranker = ItemReranker(
        ...    group_col="group_id", rec_col="rec", score_col="score",
        ...    target_prefix="11", weight=2.0,
        ... )
        >>> rec_df = pd.DataFrame(
        ...    [
        ...        [1, ["101", "111", "121"], [3, 2, 1]],
        ...        [2, ["131", "141", "151"], [3, 2, 1]]
        ...    ],
        ...    columns = ["group_id", "rec", "score"],
        ... )
        >>> item_reranker.transform(data=rec_df,
        ...                         reranker_candidate_count=3,
        ...                         provide_score=True,)
           group_id              rec        score
        0         1  [111, 101, 121]  [4.0, 3, 1]
        1         2  [131, 141, 151]    [3, 2, 1]
        """
        super().transform(data)

        assert self.group_col in data, "data must have the given group_col"
        assert self.rec_col in data, "data must have the given rec_col"
        assert self.score_col in data, "data must have the given score_col"
        assert output_format in [
            "dataframe",
            "json",
        ], "output_format should be 'dataframe' or 'json'"
        assert isinstance(provide_score, bool), "provide_score must be bool"
        assert (
            isinstance(reranker_candidate_count, int) and reranker_candidate_count > 0
        ), "reranker_candidate_count must be a positive integer"

        # deep copy dataframe with lists
        self.data = data.copy(deep=True)
        self.data[self.rec_col] = data[self.rec_col].apply(lambda x: copy.deepcopy(x))
        self.data[self.score_col] = data[self.score_col].apply(
            lambda x: copy.deepcopy(x)
        )

        # combine rec and score columns, get new scores and rerank them
        self.data = self.data.apply(self._prioritize, axis=1)

        # filter top k results within each group by given candidate count
        self.data[self.rec_col] = self.data[self.rec_col].apply(
            lambda x: x[:reranker_candidate_count]
        )
        self.data[self.score_col] = self.data[self.score_col].apply(
            lambda x: x[:reranker_candidate_count]
        )

        if provide_score:
            self.data = self.data[[self.group_col, self.rec_col, self.score_col]]
        else:
            self.data = self.data[[self.group_col, self.rec_col]]

        if output_format == "dataframe":
            return self.data
        elif output_format == "json":
            return self.data.to_dict("records")

    def _type_checking(self):
        super()._type_checking()
        assert isinstance(self.group_col, str), "group_col must be str"
        assert isinstance(self.rec_col, str), "rec_col must be str"
        assert isinstance(self.score_col, str), "score_col must be str"
        assert isinstance(self.target_prefix, str), "target_prefix must be str"
        assert isinstance(self.weight, float), "weight must be float"

    # reorder the rec and score lists by given prefix and weight
    def _prioritize(self, row):
        # weight items with the given prefix
        for i in range(len(row[self.rec_col])):
            if (
                str(row[self.rec_col][i])[: len(self.target_prefix)]
                == self.target_prefix
            ):
                row[self.score_col][i] *= self.weight

        # combine rec and score lists and rank them with new scores
        rec_score_list = zip(row[self.rec_col], row[self.score_col])
        rec_score_list = sorted(
            rec_score_list,
            key=lambda x: (x[1], x[0][: len(self.target_prefix)] == self.target_prefix),
            reverse=True,
        )
        # decompose the combined list into rec and score lists
        rec_score_list = list(zip(*rec_score_list))
        row[self.rec_col] = list(rec_score_list[0])
        row[self.score_col] = list(rec_score_list[1])
        return row
