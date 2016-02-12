import requests
import json
from collections import OrderedDict


class LimeSurveyRemoteControl2API(object):

    def __init__(self, url):
        self.url = url
        self.headers = {"content-type": "application/json"}
        self.utils = _Utils(self)
        self.sessions = _Sessions(self)
        self.surveys = _Surveys(self)
        self.tokens = _Tokens(self)
        self.questions = _Questions(self)


class _Utils(object):

    def __init__(self, lime_survey_api):
        self.api = lime_survey_api
    
    def request(self, data, url=None, headers=None):
        """
        Return the result of an API call, or None.

        Exceptions are logged rather than raised.

        Parameters
        :param data: Method name and parameters to send to the API.
        :type data: String
        :param url: Location of the LimeSurvey API endpoint.
        :type url: String
        :param headers: HTTP headers to add to the request.
        :type headers: Dict

        Return
        :return: Dictionary containing result of API call, or None.
        """
        if url is None:
            url = self.api.url
        if headers is None:
            headers = self.api.headers
        return_value = None
        try:
            response = requests.post(url, headers=headers, data=data)
            if len(response.content) > 0:
                return_value = response.json()
        except requests.ConnectionError as pe:
            # TODO: some handling here
            return_value = None
        return return_value

    @staticmethod
    def prepare_params(method, params):
        """
        Prepare remote procedure call parameter dictionary.

        Important! Despite being provided as key-value, the API treats all
        parameters as positional. OrderedDict should be used to ensure this,
        otherwise some calls may randomly fail.

        Parameters
        :param method: Name of API method to call.
        :type method: String
        :param params: Parameters to the specified API call.
        :type params: OrderedDict

        Return
        :return: JSON encoded string with method and parameters.
        """
        data = OrderedDict([
            ('method', method),
            ('params', params),
            ('id', 1)
        ])
        data_json = json.dumps(data)
        return data_json


class _Sessions(object):

    def __init__(self, lime_survey_api):
        self.api = lime_survey_api

    def get_session_key(self, username, password):
        """
        Get a session key for all subsequent API calls.

        Parameters
        :param username: LimeSurvey username to authenticate with.
        :type username: String
        :param password: LimeSurvey password to authenticate with.
        :type password: String
        """
        params = OrderedDict([
            ("username", username),
            ("password", password)
        ])
        data = self.api.utils.prepare_params('get_session_key', params)
        response = self.api.utils.request(data)
        return response

    def release_session_key(self, session_key):
        """
        Close an open session.
        """
        params = {'sSessionKey': session_key}
        data = self.api.utils.prepare_params('release_session_key', params)
        response = self.api.utils.request(data)
        return response


class _Surveys(object):

    def __init__(self, lime_survey_api):
        self.api = lime_survey_api

    def list_surveys(self, session_key, username):
        """
        List surveys accessible to the specified username.

        Parameters
        :param session_key: Active LSRC2 session key
        :type session_key: String
        :param username: LimeSurvey username to list accessible surveys for.
        :type username: String
        """
        params = OrderedDict([
            ('sSessionKey', session_key),
            ('iSurveyID', username)
        ])
        data = self.api.utils.prepare_params('list_surveys', params)
        response = self.api.utils.request(data)
        return response


class _Tokens(object):

    def __init__(self, lime_survey_api):
        self.api = lime_survey_api

    def add_participants(self, session_key, survey_id, participant_data,
                         create_token_key=True):
        """
        Add participants to the specified survey.

        Parameters
        :param session_key: Active LSRC2 session key
        :type session_key: String
        :param survey_id: ID of survey to delete participants from.
        :type survey_id: Integer
        :param participant_data: List of participant detail dictionaries.
        :type participant_data: List[Dict]
        """
        params = OrderedDict([
            ('sSessionKey', session_key),
            ('iSurveyID', survey_id),
            ('aParticipantData', participant_data),
            ('bCreateToken', create_token_key)
        ])
        data = self.api.utils.prepare_params('add_participants', params)
        response = self.api.utils.request(data)
        return response

    def delete_participants(self, session_key, survey_id, tokens):
        """
        Delete participants (by token) from the specified survey.

        Parameters
        :param session_key: Active LSRC2 session key
        :type session_key: String
        :param survey_id: ID of survey to delete participants from.
        :type survey_id: Integer
        :param tokens: List of token IDs for participants to delete.
        :type tokens: List[Integer]
        """
        params = OrderedDict([
            ('sSessionKey', session_key),
            ('iSurveyID', survey_id),
            ('aTokenIDs', tokens)
        ])
        data = self.api.utils.prepare_params('delete_participants', params)
        response = self.api.utils.request(data)
        return response


class _Questions(object):

    def __init__(self, lime_survey_api):
        self.api = lime_survey_api

    def list_questions(self, session_key, survey_id,
                       group_id=None, language=None):
        """
        Return a list of questions from the specified survey.

        Parameters
        :param session_key: Active LSRC2 session key
        :type session_key: String
        :param survey_id: ID of survey to list questions from.
        :type survey_id: Integer
        :param group_id: ID of the question group to filter on.
        :type group_id: Integer
        :param language: Language of survey to return for.
        :type language: String
        """

        params = OrderedDict([
            ('sSessionKey', session_key),
            ('iSurveyID', survey_id),
            ('iGroupID', group_id),
            ('sLanguage', language)
        ])
        data = self.api.utils.prepare_params('list_questions', params)
        response = self.api.utils.request(data)
        return response
