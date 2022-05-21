import json
import operator

from app.main import create_app
from app.main.model.crm import (
    PersonalizedScores,
)
from app.main.util.test_connection import (
    create_connection,
    disconnection,
)

client = create_app(config_name="test").test_client()


class TestCRMController:
    def test_personalized_scores(self):
        connection = create_connection(db_alias="crm_db")
        personalized_scores = PersonalizedScores(
            customer_email="email", ACM_FLG="N", BULK_FLAG="Y"
        )
        personalized_scores.save()
        expect = {
            "customer_email": "email",
            "ACM_FLG": "N",
            "BULK_FLAG": "Y",
        }

        response = client.get(f"/api/rec/crm/personalized_scores?customer_email=email")

        personalized_scores.delete()
        disconnection(connection)
        assert operator.eq(expect, json.loads(response.data.decode("utf-8")))

    def test_personalized_scores_404(self):
        connection = create_connection(db_alias="crm_db")

        response = client.get(f"/api/rec/crm/personalized_scores?customer_email=email")

        disconnection(connection)
        assert response.status_code == 404

    def test_personalized_scores_bad_request(self):
        connection = create_connection(db_alias="crm_db")

        response = client.get(f"/api/rec/crm/personalized_scores")

        disconnection(connection)
        assert response.status_code == 400
