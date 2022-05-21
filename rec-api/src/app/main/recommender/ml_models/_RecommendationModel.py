"""
This module provides the parent class for all recommendation models.
"""
import inspect
from abc import ABC
from abc import abstractmethod

import pandas as pd


class _RecommendationModel(ABC):
    """
    Helper class that provides a standard way to create an RecommendationModel using
    inheritance.
    """

    def __init__(self):
        # get parameter names
        signature = inspect.signature(self.__init__)
        self.param_names = list(signature.parameters.keys())

    def __repr__(self):
        param_list = ", ".join(
            [name + "=" + str(getattr(self, name)) for name in self.param_names]
        )
        return self.__class__.__name__ + "(" + param_list + ")"

    def set_param(self, **params):
        """This method sets parameters within the instance."""
        if params:
            valid_params = self.param_names
            param_dic = {}
            for valid_param in valid_params:
                param_dic[valid_param] = getattr(self, valid_param)
            try:
                for key, value in params.items():
                    assert key in valid_params, "invalid parameter"
                    setattr(self, key, value)
                self._type_checking()
            except AssertionError as e:
                for valid_param in valid_params:
                    setattr(self, valid_param, param_dic[valid_param])
                raise e

        return self

    @abstractmethod
    def fit(self, data: pd.DataFrame):
        # check the type of the input
        assert isinstance(data, pd.DataFrame), "data must be DataFrame"

    @abstractmethod
    def predict(
        self,
        candidate_count: int,
        output_format: str = "json",
        provide_score: bool = False,
        rec_col: str = "recommendations",
        score_col: str = "score",
    ):
        """
        Parameters
        ----------
        candidate_count: int
            The returned recommendations count
        output_format: str
            The format of returned result. Should be json or dataframe
        provide_score: bool
            Whether provide recommendation score in returned result
        rec_col
            The recommendation column's name in returned result
        score_col
            The recommendation score column's name in returned result

        """
        # check the types of inputs
        self._predict_input_type_checking(
            candidate_count, output_format, provide_score, rec_col, score_col
        )

    @abstractmethod
    def _type_checking(self):
        """This method checks the types of the inputs."""
        pass

    @staticmethod
    def _predict_input_type_checking(
        candidate_count, output_format, provide_score, rec_col, score_col
    ):
        """This method checks the types of the inputs of predict function"""
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

    @staticmethod
    def _format_transform(df, output_format):
        """This method transforms the format of the output."""
        if output_format == "dataframe":
            return df
        elif output_format == "json":
            return df.to_dict("records")
