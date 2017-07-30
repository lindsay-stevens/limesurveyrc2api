import requests
import json
from collections import OrderedDict
from limesurveyrc2api.exceptions import LimeSurveyError
from limesurveyrc2api._survey import _Survey
from limesurveyrc2api._token import _Token


class LimeSurvey(object):

    def __init__(self, url, username):
        self.headers = {"content-type": "application/json"}
        self.url = url
        self.username = username
        self.session_key = None
        self.survey = _Survey(self)  # Setup and admin of surveys.
        self.token = _Token(self)    # Participants and their data.

    def open(self, password):
        """
        Open a session in LimeSurvey.

        Parameters
        :param password: LimeSurvey password to authenticate with.
        :type password: String
        """
        method = "get_session_key"
        params = OrderedDict([
            ("username", self.username),
            ("password", password)
        ])
        response = self.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = ["Invalid user name or password"]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)
        else:
            assert response_type is str
        self.session_key = response

    def query(self, method, params):
        """
        Query the LimeSurvey API

        Important! Despite being provided as key-value, the API treats all
        parameters as positional. OrderedDict should be used to ensure this,
        otherwise some calls may randomly fail.

        Parameters
        :param method: Name of API method to call.
        :type method: String
        :param params: Parameters to the specified API call.
        :type params: OrderedDict

        Return
        :return: result of API call
        :raise: requests.ConnectionError
        :raise: LimeSurveyError if the API returns an error (either http error
            or error message in body)
        """
        if not self.session_key and not method == "get_session_key":
            raise LimeSurveyError(method, "No session open", params)

        # 1. Prepare the request data
        data = OrderedDict([
            ("method", method),
            ("params", params),
            ("id", 1)  # Possibly a request id for parallel use cases.
        ])
        data_json = json.dumps(data)

        # 2. Query the API
        response = requests.post(
            self.url, headers=self.headers, data=data_json)

        if not response.ok:
            raise LimeSurveyError(
                method, "Not response.ok", response.status_code,
                response.content)

        if not 0 < len(response.content):
            raise LimeSurveyError(
                method, "Not 0 < len(response.content)",
                response.status_code, response.content)

        response_data = response.json()

        try:
            return_value = response_data.get("result")
        except KeyError:
            raise LimeSurveyError(
                method, "Key 'result' not in response json",
                response.status_code, response.content)

        return return_value

    def close(self):
        """
        Close an open session in LimeSurvey.
        """
        method = "release_session_key"
        params = OrderedDict([
            ("sSessionKey", self.session_key)
        ])
        response = self.query(method=method, params=params)

        if response == "OK":
            self.session_key = None
        else:
            raise LimeSurveyError(method, "Did not receive 'OK' response")

        return response
