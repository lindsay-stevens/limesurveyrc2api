from collections import OrderedDict
from limesurveyrc2api.exceptions import LimeSurveyError


class _Token(object):

    def __init__(self, api):
        self.api = api

    def add_participants(
            self, survey_id, participant_data, create_token_key=True):
        """
        Add participants to the specified survey.

        Parameters
        :param survey_id: ID of survey to delete participants from.
        :type survey_id: Integer
        :param participant_data: List of participant detail dictionaries.
        :type participant_data: List[Dict]
        :param create_token_key: If True, generate the new token instead of
          using a provided value.
        """
        method = "add_participants"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID", survey_id),
            ("aParticipantData", participant_data),
            ("bCreateToken", create_token_key)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Error: Invalid survey ID",
                "No token table",
                "No permission"
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)

        assert response_type is list
        return response

    def delete_participants(self, survey_id, tokens):
        """
        Delete participants (by token) from the specified survey.

        Parameters
        :param survey_id: ID of survey to delete participants from.
        :type survey_id: Integer
        :param tokens: List of token IDs for participants to delete.
        :type tokens: List[Integer]
        """
        method = "delete_participants"
        params = OrderedDict([
            ('sSessionKey', self.api.session_key),
            ('iSurveyID', survey_id),
            ('aTokenIDs', tokens)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Error: Invalid survey ID",
                "Error: No token table",
                "No permission",
                "Invalid Session Key"
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)

        assert response_type is dict
        return response

    def get_participant_properties(self, survey_id, token_id):
        """
        Get participant properties (by token) from the specified survey.

        For token properties, could choose from:

        ('aTokenProperties', [
                "blacklisted", "completed", "email", "emailstatus", "firstname",
                "language", "lastname", "mpid", "participant_id",
                "remindercount", "remindersent", "sent", "tid", "token",
                "usesleft", "validfrom", "validuntil"])

        Parameters
        :param survey_id: ID of survey to delete participants from.
        :type survey_id: Integer
        :param token_id: ID of survey to delete participants from.
        :type token_id: Integer
        """
        method = "get_participant_properties"
        # TODO: RPC method can accept more query params than just the token_id
        # It gets a bit more complicated to test, more possible error messages
        params = OrderedDict([
            ('sSessionKey', self.api.session_key),
            ('iSurveyID', survey_id),
            ('aTokenQueryProperties', {"tid": token_id})
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Error: Invalid survey ID",
                "Error: No token table",
                "Error: Invalid tokenid",
                "No permission",
                "Invalid Session Key"
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)

        assert response_type is dict
        return response

    def list_participants(self):
        # TODO
        pass

    def get_summary(self):
        # TODO
        pass
