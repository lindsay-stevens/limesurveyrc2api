import requests
import json
from collections import OrderedDict


class LimeSurveyError(Exception):
    """Base class for exceptions in LimeSurvey."""
    pass


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
        # 1. Prepare the request data
        data = OrderedDict([
            ('method', method),
            ('params', params),
            ('id', 1)  # Query ID - corresponding response will have the same ID
        ])
        # 2. Query the API
        response = requests.post(self.api.url, headers=self.api.headers, data=json.dumps(data))
        response_content = response.json()

        # 3. Evaluate the response
        if not response.ok or response_content.get('error'):
            raise LimeSurveyError(
                "Error during query to '{}':{} {}".format(
                    self.api.url, response.status_code, response_content))

        return response_content


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
        return self.api.utils.query('get_session_key', params)

    def release_session_key(self, session_key):
        """
        Close an open session.
        """
        params = {'sSessionKey': session_key}
        return self.api.utils.query('release_session_key', params)


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
        return self.api.utils.query('list_surveys', params)

    def get_summary(self, session_key, survey_id):
        """
        Get participant properties in a survey.

        Parameters
        :param session_key: Active LSRC2 session key
        :type session_key: String
        :param survey_id: ID of survey
        :type survey_id: Integer

        :return: dict with keys 'token_count', 'token_invalid', 'token_sent',
            'token_opted_out', and 'token_completed' with strings as values.
        """
        params = OrderedDict([
            ('sSessionKey', session_key),
            ('iSurveyID', survey_id)
        ])
        return self.api.utils.query('get_summary', params)


class _Tokens(object):

    def __init__(self, lime_survey_api):
        self.api = lime_survey_api

    def get_participant_properties(self, session_key, survey_id, token_id):
        """
        Get participant properties in a survey.

        Parameters
        :param session_key: Active LSRC2 session key
        :type session_key: String
        :param survey_id: ID of survey
        :type survey_id: Integer
        :param token_id: ID of the token to lookup
        :type token_id: Integer

        :return: Dict with all participant properties
        """
        params = OrderedDict([
            ('sSessionKey', session_key),
            ('iSurveyID', survey_id),
            ('aTokenQueryProperties', {'tid': token_id})
        ])
        return self.api.utils.query('get_participant_properties',
                                             params)

    def list_participants(self, session_key, survey_id, start=0, limit=1000,
                          ignore_token_used=False, attributes=False,
                          conditions=None):
        """
        List participants in a survey.

        Parameters
        :param session_key: Active LSRC2 session key
        :type session_key: String
        :param survey_id: ID of survey
        :type survey_id: Integer
        :param start: Index of first token to retrieve
        :type start: Integer
        :param limit: Number of tokens to retrieve
        :type limit: Integer
        :param ignore_token_used: If True, tokens that have been used are not
            returned
        :type ignore_token_used: Integer

        :param attributes: The extended attributes that we want
        :type attributes: List[String]
        :param conditions: (optional) conditions to limit the list,
            e.g. {'email': 't1@test.com'}
        :type conditions: List[Dict]

        :return: List of dictionaries

        """
        conditions = conditions or []
        params = OrderedDict([
            ('sSessionKey', session_key),
            ('iSurveyID', survey_id),
            ('iStart', start),
            ('iLimit', limit),
            ('bUnused', ignore_token_used),
            ('aAttributes', attributes),
            ('aConditions', conditions)
        ])
        return self.api.utils.query('list_participants', params)

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
        return self.api.utils.query('add_participants', params)

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
        return self.api.utils.query('delete_participants', params)


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
        return self.api.utils.query('list_questions', params)
