from flask_restplus import Resource, reqparse
from flask import abort, request
from mongoengine import DoesNotExist
import app.main.util.externalized_messages as messages
from werkzeug.exceptions import NotFound, Unauthorized
from app.main.util._enum import EnumString
from app.main.util.exception_handler import NotEnoughRecommendations


class Controller(Resource):
    """
    This is the base/parent class for all controllers. The reason we use the parent class is to reduce code duplicate rate
    so the code could be passed in SonarQube.

    All controllers/resources should use this class as parent class, and pass in different arguments and service as
    parameters. All arguments, including the error messages, are saved in app.main.util.controller_args.py
    """

    def __init__(self, args_dict, service):
        Resource.__init__(self)
        self.args_dict = args_dict
        self.service = service

    def get(self):
        args = self._get_args()
        self._validate_args(args)

        try:
            result = self.service(**args)
            """
            If the recommendation results is a list of int or str, convert it to list of str.
            If the recommendation result is a list of dict, keep what it is.
            """
            if result and type(result) == list and not (type(result[0]) == dict):
                result = [str(x) for x in result]
            return result
        except Unauthorized:
            abort(401, description=messages.error_messages["unauthorized_access"])
        except DoesNotExist:
            abort(404, description=self.args_dict["error_message"])
        except NotFound:
            abort(404, description=self.args_dict["error_message"])
        except IndexError:
            abort(500, description=messages.error_messages["index_error"])
        except AssertionError:
            abort(416, description=messages.error_messages["assertion_error"])
        except ValueError:
            abort(416, description=messages.error_messages["value_error"])
        except NotEnoughRecommendations:
            abort(
                416, description=messages.error_messages["not_enough_recommendations"]
            )
        except Exception:
            abort(500, description=messages.error_messages["internal_error"])

    def put(self):
        args = self._get_args()
        self._validate_args(args)

        try:
            result = self.service(**args)
            return result
        except DoesNotExist:
            abort(404, description=self.args_dict["error_message"])
        except Exception:
            abort(500, description=messages.error_messages["internal_error"])

    def post(self):
        args = request.json
        if not args:
            abort(400, description="Bad Request: No Input data provided")
        try:
            result = self.service(args)
            return result
        except DoesNotExist:
            abort(404, description=self.args_dict["error_message"])
        except Exception:
            abort(500, description=messages.error_messages["internal_error"])

    def _get_args(self):
        # Build the request parser and get arguments
        parser = reqparse.RequestParser()
        for key, val in self.args_dict.items():
            # If it's not error message, add the argument to parser
            if key != EnumString.error_message.value:
                parser.add_argument(
                    key,
                    type=val["type"],
                    required=val["required"],
                    help=val["help"],
                    location=val["location"],
                )
        args = parser.parse_args()
        return args

    def _validate_args(self, args):
        # If the argument doesn't provide, set it to be the default value
        for key, val in args.items():
            if val is None and "default" in self.args_dict[key]:
                args[key] = self.args_dict[key]["default"]


class WordEmbeddingController(Controller):
    """
    This is the parent class for all WordEmbedding related controllers
    """

    def get(self):
        args = super()._get_args()
        super()._validate_args(args)
        try:
            result = self.service(**args)
            return result
        except Exception:
            abort(500, description=messages.error_messages["internal_error"])
