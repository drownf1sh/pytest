"""
This module provides the parent class for all recommendation models.
"""
import inspect
from abc import ABC
from abc import abstractmethod

import pandas as pd


class _Processor(ABC):
    """
    Helper class that provides a standard way to create an _Processor using
    inheritance.
    """

    def __init__(self):
        """Initialize parameters"""
        # get parameter names
        signature = inspect.signature(self.__init__)
        self.param_names = list(signature.parameters.keys())

    def __repr__(self):
        """Refactor to represent transformer name and parameters"""
        param_list = ", ".join(
            [name + "=" + str(getattr(self, name)) for name in self.param_names]
        )
        return self.__class__.__name__ + "(" + param_list + ")"

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
    def transform(self, data: pd.DataFrame):
        # check the type of the input
        assert isinstance(data, pd.DataFrame), "data must be DataFrame"

    @abstractmethod
    def _type_checking(self):
        """This method checks the types of the inputs."""
        pass
