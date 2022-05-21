import pandas as pd
import numpy as np
from app.main import text_clean
from app.main.util.global_models import (
    logistic_regression as classification_model,
    scaler,
    get_vectors,
)


def generate_categories(
    search_term: str,
    candidate_count: int,
    word_vector_length: int,
):
    """
    Get suggested categories for search terms. This service is different with others
    because of its logic and usage.

    Parameters
    ----------
    search_term: str
    The search_term used to get categories

    candidate_count: int, default=5
    The amount of suggested categories will be returned.

    word_vector_length: int
    The vector's dimension for word_embedding. Currently it's 300 dimensions for dev/prod
    and 4 dimensions for pytest.

    Return
    ------
    List of suggested categories
    """
    df = pd.DataFrame(data=np.array([search_term]), columns=["search_term"])
    # Clean search_term with text_clean
    cleaned_search_term = text_clean.transform(df)
    words_list = cleaned_search_term["search_term"][0]
    vectors = get_vectors(words=words_list)
    # Calculate the averaged vector for multi words. Currently we only use average.
    vector_array = np.zeros(word_vector_length)
    for word in vectors:
        if (len(vectors[word])) == word_vector_length:
            vector_array = vector_array + vectors[word]
    vector_array = vector_array / len(vectors)

    predict_result = pd.DataFrame(
        classification_model.predict_proba(
            scaler.fit_transform(np.array(vector_array).reshape(-1, 1)).reshape(1, -1)
        ).reshape(-1, 1),
        columns=["proba"],
    )
    predict_result["labels"] = classification_model.classes_.reshape(-1, 1)
    # Return top recommendations
    return (
        predict_result.nlargest(candidate_count, "proba")
        .sort_values(by=["proba"], ascending=False)["labels"]
        .tolist()
    )
