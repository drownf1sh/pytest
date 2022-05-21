from flask_restplus import Namespace
from app.main.controller.controller import Controller
from app.main.service import store_name_service as store_name_service
import app.main.util.externalized_messages as messages
import app.main.util.controller_args as controller_args

api = Namespace("store_name", description="Store Name Suggestion API")


@api.route("/store_name_suggestions", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_store_names"],
    type=int,
)
@api.param(name="store_name", description=messages.descriptions["store_name"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.store_name_args["error_message"],
        example_value=messages.example_format["store_name_suggestion"],
    )
)
@api.doc(security="fgm_token")
class SuggestedStoreName(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.store_name_args,
        service=store_name_service.get_store_name_suggestions,
    ):
        Controller.__init__(self, args_dict, service)
