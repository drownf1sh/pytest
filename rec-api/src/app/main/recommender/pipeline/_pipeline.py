"""
This module provides the parent class for all recommendation models.
"""
import inspect
from abc import ABC
from abc import abstractmethod

import pandas as pd

from app.main.recommender.ml_models._RecommendationModel import _RecommendationModel
from app.main.recommender.features._processor import _Processor
from app.main.recommender.features._transformer import _Transformer


class _Pipeline(ABC):
    """
    Helper class that provides a standard way to create a Pipeline using
    inheritance.
    """

    def __init__(self, stages: list = None):
        """Initialize parameters

        Parameters
        ----------
        stages: list, default = None
            input transformers
        """
        # get parameter names
        signature = inspect.signature(self.__init__)
        self.param_names = list(signature.parameters.keys())
        self.intermediate_output_format = None
        self.intermediate_provide_score = None
        self.rec_col = None
        self.score_col = None

    def set_param(self, **params):
        """This method sets parameters within the instance."""
        if params:
            valid_params = self.param_names
            for key, value in params.items():
                assert key in valid_params, "invalid parameter"
                setattr(self, key, value)

            self._type_checking()
        return self

    @abstractmethod
    def fit(self, data: pd.DataFrame):
        """
        This method fits the model with the given data.

        Parameters
        ----------
        data: pd.DataFrame
            Provide the data
        """
        # check the type of the input
        assert isinstance(data, pd.DataFrame), "data must be DataFrame"

        self.feature_df = data.copy()

        if self.stages is not None:
            for stage in self.stages:
                if isinstance(stage, _Processor):
                    self.feature_df = stage.transform(self.feature_df)
                else:
                    self.feature_df = stage.fit_transform(self.feature_df)

        return self

    @abstractmethod
    def predict(
        self,
        candidate_count: int = 5,
        output_format: str = "json",
        provide_score: bool = False,
        rec_col: str = "recommendations",
        score_col: str = "score",
        reranker_candidate_count: int = 5,
    ):
        """
        This method provides a final recommendation based on the result from the model.

        Parameters
        ----------
        candidate_count: int, default = 5
            Define how many recommendations that the rec model will provide
        output_format: str, default = "json"
            the output format, options are "json" or "dataframe"
        provide_score: bool, default = False
            output score when condition is True
        rec_col: str, default = "recommendations"
            The recommendations column in the result
        score_col: str, default = "score"
            The score column in the result
        reranker_candidate_count: int, default = 5
            Define how many recommendations that the reranker will provide
        """
        # check the types of inputs
        assert (
            isinstance(candidate_count, int) and candidate_count >= 0
        ), "candidate_count must be non-negative integer"
        assert output_format in [
            "dataframe",
            "json",
        ], "output_format should be 'dataframe' or 'json'"
        assert isinstance(provide_score, bool), "provide_score must be bool"
        assert isinstance(rec_col, str), "rec_col must be str"
        assert isinstance(score_col, str), "score_col must be str"
        assert (
            isinstance(reranker_candidate_count, int) and reranker_candidate_count >= 0
        ), "reranker_candidate_count must be non-negative integer"

        # If pipeline has reranker, then need to hard code the model's predicted result
        # to be dataframe, and provide_score to be true, otherwise use the parameter
        # that pipeline passed in
        if self.reranker:
            self.intermediate_output_format = "dataframe"
            self.intermediate_provide_score = True
        else:
            self.intermediate_output_format = output_format
            self.intermediate_provide_score = provide_score

        self.rec_col = rec_col
        self.score_col = score_col

    @abstractmethod
    def _type_checking(self):
        """This method checks the types of the inputs."""
        assert isinstance(
            self.model, _RecommendationModel
        ), "model must be _RecommendationModel"
        if self.stages is not None:
            assert isinstance(self.stages, list), "stages must be a list"
            for stage in self.stages:
                assert isinstance(
                    stage, (_Transformer, _Processor)
                ), "stages should only contain transformers and processors"
