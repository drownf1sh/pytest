"""
Initialize classification model, the standard scaler, and the get_vectors function
"""
import sys
from app.main.util.model_storage import load_model
from app.main.util._test_data_and_object import (
    trained_logistic_regression_model,
    trained_standard_scaler,
    get_test_word_vectors,
    MockCBFPipeline,
)
from app.main.service.word_embedding_service import get_vectors_for_word_lists

if "pytest" in sys.modules:
    scaler = trained_standard_scaler()
    logistic_regression = trained_logistic_regression_model(scaler=scaler)
    get_vectors = get_test_word_vectors
    # cbf_pipeline = MockCBFPipeline()
else:
    db_name = "mongo_rec"
    collection_name = "recModels"
    logistic_regression = load_model(
        db_name=db_name, collection_name=collection_name, model="logistic_regression"
    )

    scaler = load_model(
        db_name=db_name, collection_name=collection_name, model="StandardScaler"
    )

    # cbf_pipeline = load_model(
    #     db_name=db_name, collection_name=collection_name, model="cbf_pipeline"
    # )

    get_vectors = get_vectors_for_word_lists
