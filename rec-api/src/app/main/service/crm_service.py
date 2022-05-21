import json
from mongoengine import DoesNotExist
from app.main.model.crm import (
    PersonalizedScores,
)


def get_crm_personalized_scores_service(**kwargs):
    """
    Search the database to get personalized scores by given custom email.
    :param customer_email: str
    :return: a dict obj
    """
    customer_email = kwargs["customer_email"]

    try:
        personalized_scores_object = (
            PersonalizedScores.objects(customer_email=customer_email)
            .exclude("id")
            .get()
        )
    except DoesNotExist as e:
        raise e

    return json.loads(personalized_scores_object.to_json())
