from flask_restplus import Namespace, Resource
from werkzeug.exceptions import BadRequest
from flask import abort
from ..util.environment_variables import *

api = Namespace(
    "ping",
    description="Confirm that the API has started successfully and to confirm the currently "
    "deployed version",
)


@api.route("")
class Ping(Resource):
    @api.doc(responses={200: "Success", 400: "Environment Error"})
    def get(self):
        """
        This endpoint to confirm confirm that the API has started successfully and to confirm the currently deployed version
        """
        try:
            response = {
                "app_name": APP_PROJ + "-" + APP_ENV + "-" + APP_NAME,
                "version": APP_VERSION,
            }
            return response
        except EnvironmentError as err:
            abort(400, BadRequest(err))
