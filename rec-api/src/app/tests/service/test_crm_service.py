import operator
import pytest
from mongoengine import DoesNotExist
from app.main.model.crm import (
    PersonalizedScores,
)
from app.main.util.test_connection import (
    create_connection,
    disconnection,
)
from app.main.service.crm_service import get_crm_personalized_scores_service


class TestCRMService:
    def test_crm_personalized_scores_service(self):
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
        result = get_crm_personalized_scores_service(customer_email="email")
        personalized_scores.delete()
        disconnection(connection)
        assert operator.eq(expect, result)

    def test_get_crm_personalized_scores_service_failed(self):
        connection = create_connection(db_alias="crm_db")
        with pytest.raises(DoesNotExist) as excinfo:
            get_crm_personalized_scores_service(customer_email="email")
        disconnection(connection)
        assert str(excinfo.value) == "PersonalizedScores matching query does not exist."
