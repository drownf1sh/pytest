import json
import operator
from unittest import mock

import pytest

from app.main import create_app
from app.main.model.synonyms import SynonymsWords
from app.main.util.test_connection import create_connection, disconnection

client = create_app(config_name="test").test_client()


class TestStoreNameController:
    @mock.patch(
        "app.main.components.dup_store_name_handler.store_names_client", autospec=True
    )
    def test_suggested_store_name_valid_token(self, mock_store_names_client):
        connection = create_connection()
        synonyms_word = SynonymsWords(search_word="word")
        synonyms_word.save()

        store_names = ["design", "shop", "store"]
        mock_store_names_client.add_store_names.return_value = store_names
        headers = {
            "Accept": "application/json",
            "Authorization": "eyJhbGciOiJIUzUxMiJ9.eyJjbGllbnRJZCI6InVzciIsIl91c2VySWQiOiIxMjQxODA5MTE3NzUxIiwiX3NlbGxlclN0b3JlSWQiOm51bGwsIl9kZXZpY2VVdWlkIjoiOGU1NjA0YWYtOTlkYi00N2E1LWI1ZTktNDY1MDQwNDg2NjkwIiwiX2RldmljZU5hbWUiOiJDaHJvbWUiLCJfY3JlYXRlVGltZSI6IjE2NDkxODc0MzY5MjAiLCJfZXhwaXJlVGltZSI6IjE2NTE3Nzk0MzY5MjAiLCJzdWIiOiIxMjQxODA5MTE3NzUxIiwiaWF0IjoxNjQ5MTg3NDM2LCJleHAiOjE2NTE3Nzk0MzYsImF1ZCI6InVzZXIiLCJqdGkiOiJCOHUwU3NMbVM2QjZXa3MwOXc2WWZVeWRtSWhyc1RQayJ9.32YC90z7ZpXYIxOZ5F1NPgvLtW3CkdTBGWrlFfwgoZJwpA0n6hvbRQ4JpCiDR5Jq1ufyEAJ8sX55XLGVN7ojNQ",
        }
        response = client.get(
            f"/api/rec/store_name/store_name_suggestions?store_name=a&candidate_count=2",
            headers=headers,
        )
        expect = ["a design", "a shop"]
        disconnection(connection)
        assert operator.eq(expect, json.loads(response.data))

    @mock.patch(
        "app.main.components.dup_store_name_handler.profanity_screen_word",
        autospec=True,
    )
    def test_suggested_store_name_unauthorized_token(self, mock_profanity_screen_word):
        connection = create_connection()
        synonyms_word = SynonymsWords(search_word="word")
        synonyms_word.save()

        mock_profanity_screen_word.return_value = [{"A": 1}]
        headers = {"Accept": "application/json", "Authorization": "invalid token"}
        response = client.get(
            f"/api/rec/store_name/store_name_suggestions?store_name=a&candidate_count=2",
            headers=headers,
        )
        expect = {"message": "Unauthorized access"}
        disconnection(connection)
        assert response.status_code == 401
        assert operator.eq(expect, json.loads(response.data))


if __name__ == "__main__":
    pytest.main()
