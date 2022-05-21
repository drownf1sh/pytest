"""
Customer Relationship Management (CRM) project API controller module
"""
from flask_restplus import Namespace
from app.main.controller.controller import Controller
from app.main.service import crm_service
import app.main.util.externalized_messages as messages
import app.main.util.controller_args as controller_args

api = Namespace("crm", description="CRM recommendation api")


@api.route("/personalized_scores", methods=["GET"])
@api.param(
    name="customer_email", description=messages.descriptions["customer_email"], type=str
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.crm_args["personalized_scores_args"]["error_message"],
        example_value=messages.example_format["personalized_scores_suggestion"],
    )
)
class PersonalizedScores(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.crm_args["personalized_scores_args"],
        service=crm_service.get_crm_personalized_scores_service,
    ):
        Controller.__init__(self, args_dict, service)
