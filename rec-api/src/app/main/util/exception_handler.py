import http


class NotEnoughRecommendations(Exception):
    """
    Raises exceptions with not enough recommendations message
    """

    status_code = http.HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE
    detail = "Not enough recommendations"
