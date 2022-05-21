"""
This module provides pipelines to enable users to
combine text preprocessing, text feature engineering,
and content-based filtering model together as a pipeline.
"""
import pandas as pd

from app.main.recommender.pipeline._pipeline import _Pipeline
from app.main.recommender.ml_models._content_based_filtering import (
    _RecommendationModel,
    ContentBasedFiltering,
    StreamingContentBasedFiltering,
)
from app.main.recommender.postprocess._item_reranker import ItemReranker


class CBFPipeline(_Pipeline):
    """
    Class that provides the content-based filtering pipeline.
    """

    def __init__(
        self,
        item_col: str,
        stages: list = None,
    ):
        """Initialize parameters

        Parameters
        ----------
        item_col: str
            specify the item column in the input data
        stages: list, default = None
            input transformers
        model: default = ContentBasedFiltering()
            input a model
        Example
        -------
        >>> import pandas as pd
        >>> from app.main.recommender.features._text import TextClean, TextCombine
        >>> from app.main.recommender.features._word_embedding_api import WordEmbeddingApi
        >>> from app.main.recommender.features._cluster_labeler import KMeansLabeler
        >>> from app.main.recommender.ml_models._content_based_filtering import StreamingContentBasedFiltering
        >>> from app.main.recommender.pipeline._cbf_pipeline import CBFPipeline
        >>> item_df = pd.DataFrame([
        ...                         ['item1', 'a pen', 'office', ],
        ...                         ['item2', 'a pencil', 'office', ],
        ...                         ['item3', 'a notebook', 'office', ],
        ...                         ['item4', 'a mac pro notebook', 'electronic', ],
        ...                         ['item5', 'a bag of paper', 'office', ],
        ...                         ],
        ...                         columns=['item', 'description1', 'description2'])
        >>> clean = TextClean(["description1", "description2"])
        >>> combine = TextCombine(["description1", "description2"], "combine")
        >>> vectorizer = Vectorizer("tfidf", "combine")
        >>> labeler = KMeansLabeler(random_state=0)
        >>> model = DiverseContentBasedFiltering(labeler)
        >>> pipeline = CBFPipeline(item_df["item"],[clean,combine,vectorizer],model)
        >>> pipeline = pipeline.fit(item_df)
        >>> pipeline.predict(item_df, 3, "item1", label_df, 0.7)
        [{'item_id': 'item1',
          'recommendations': ['item3', 'item2', 'item5'],
        }]
        """
        super().__init__(stages)
        # globalize the variables
        for name in self.param_names:
            setattr(self, name, locals()[name])

        self.feature_df = pd.DataFrame()
        self.model = None
        self.reranker = None
        for stage in self.stages:
            if isinstance(stage, _RecommendationModel):
                self.model = stage
            if isinstance(stage, ItemReranker):
                self.reranker = stage

        if self.model:
            self.stages.remove(self.model)
        if self.reranker:
            self.stages.remove(self.reranker)

        if self.model is None:
            self.model = ContentBasedFiltering()

        self._type_checking()

    def _type_checking(self):
        super()._type_checking()
        assert isinstance(self.item_col, str), "item_col must be str"
        assert isinstance(
            self.model,
            (
                ContentBasedFiltering,
                StreamingContentBasedFiltering,
            ),
        ), (
            "model must be ContentBasedFiltering, "
            "DiverseContentBasedFiltering, "
            "or StreamingContentBasedFiltering"
        )

    def fit(self, data: pd.DataFrame):
        super().fit(data)

        # convert feature matrix to dataframe and add item id as index
        if not isinstance(self.feature_df, pd.DataFrame):
            self.feature_df = pd.DataFrame.sparse.from_spmatrix(self.feature_df)
        self.feature_df.index = data[self.item_col]

        # run model
        self.model.fit(self.feature_df)

        return self

    def predict(
        self,
        data: pd.DataFrame = None,
        candidate_count: int = 5,
        provide_score: bool = False,
        output_format: str = "json",
        rec_col: str = "recommendations",
        score_col: str = "score",
        reranker_candidate_count: int = 5,
    ):
        """
        data: pd.DataFrame, default = None
            The input dataframe to make recommendation.
            The index should be item id.
            StreamingContentBasedFiltering must provide data.

        Returns
        -------
        result: list or pd.DataFrame
            Provide top similar items in the same cluster and
            different clusters.
        """
        super().predict(
            candidate_count=candidate_count,
            output_format=output_format,
            provide_score=provide_score,
            rec_col=rec_col,
            score_col=score_col,
            reranker_candidate_count=reranker_candidate_count,
        )

        if data is not None:
            predict_data = data.copy()

            if self.stages is not None:
                for stage in self.stages:
                    predict_data = stage.transform(predict_data)
            # convert feature matrix to dataframe and add item id as index
            if not isinstance(predict_data, pd.DataFrame):
                predict_data = pd.DataFrame.sparse.from_spmatrix(predict_data)
            predict_data.index = data[self.item_col]
        else:
            predict_data = None

        target_item_pipeline_common_params = {
            "candidate_count": candidate_count,
            "provide_score": self.intermediate_provide_score,
            "output_format": self.intermediate_output_format,
            "rec_col": rec_col,
            "score_col": score_col,
        }

        # apply prediction function
        unreranked_result = self.model.predict(
            data=predict_data, **target_item_pipeline_common_params
        )

        if self.reranker:
            reranked_result = self.reranker.transform(
                unreranked_result,
                provide_score=provide_score,
                output_format=output_format,
                reranker_candidate_count=reranker_candidate_count,
            )
            return reranked_result
        else:
            return unreranked_result

    predict.__doc__ = _Pipeline.predict.__doc__ + predict.__doc__
