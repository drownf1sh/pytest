"""
This module is used to generate simple Logistic Regression model and training data to
test mktplace_service.get_search_term_categories. Since currently Flask doesn't support
function & object as parameter type, so we can't pass them as args to service from
controller. It's not the perfect practice but it's the best one for current situation.
"""
import numpy as np
import pandas as pd
import math
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def generate_model_train_data():
    x_train = [np.array([1, 1, 1, 1]), np.array([2, 8, 9, 3]), np.array([2, 3, 4, 5])]

    y_train = pd.Series(
        data={
            1: "Papercraft//Planners//Stickers",
            2: "Party//Holiday Parties//Christmas Party",
            3: "Papercraft//Cricut//Cricut Materials",
        }
    )

    return x_train, y_train


def get_test_word_vectors(words):
    return {"paint": np.array([2, 8, 9, 3])}


def trained_standard_scaler():
    scaler = StandardScaler()
    x_train, _ = generate_model_train_data()
    scaler.fit(x_train)
    return scaler


def trained_logistic_regression_model(scaler):
    logisticReg = LogisticRegression()
    x_train, y_train = generate_model_train_data()
    logisticReg.fit(scaler.transform(x_train), y_train)
    return logisticReg


class MockCBFPipeline:
    def predict(self, df: pd.DataFrame, candidate_count: int):
        item_number = df["sku_number"].loc[0]
        recommendations = [1001, 1002, 1003, 1004, 1005, 2001, 2002, 2003, 2004, 2005][
            :candidate_count
        ]
        result = [
            {
                "item_id": item_number,
                "recommendations": recommendations,
            }
        ]
        return result
