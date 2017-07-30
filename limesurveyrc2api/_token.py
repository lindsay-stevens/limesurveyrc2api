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
        :type create_token_key: Bool
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

    def delete_participants(self, survey_id, token_ids):
        """
        Delete participants (by token) from the specified survey.

        Parameters
        :param survey_id: ID of survey to delete participants from.
        :type survey_id: Integer
        :param token_ids: List of token IDs for participants to delete.
        :type token_ids: List[Integer]
        """
        method = "delete_participants"
        params = OrderedDict([
            ('sSessionKey', self.api.session_key),
            ('iSurveyID', survey_id),
            ('aTokenIDs', token_ids)
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

    def get_participant_properties(
            self, survey_id, token_id, token_query_dict=None):
        """
        Get participant properties (by token) from the specified survey.

        Provide either token_id or token_query_dict, not both.

        For token properties for querying and return, choose from:

        ["blacklisted", "completed", "email", "emailstatus", "firstname",
         "language", "lastname", "mpid", "participant_id", "remindercount",
         "remindersent", "sent", "tid", "token", "usesleft", "validfrom",
         "validuntil"]

        Parameters
        :param survey_id: ID of survey to get participant properties for.
        :type survey_id: Integer
        :param token_id: ID of participant to get properties for.
        :type token_id: Integer
        :param token_query_dict: Key(s) / value(s) to use for finding the
          participant among all those that are in the survey.
        :type token_query_dict: Dict[String, Any]
        """
        method = "get_participant_properties"
        if token_query_dict is None:
            token_query_dict = {"tid": token_id}
        if token_id is not None and token_query_dict is not None:
            raise ValueError(
                "Provide either token_id or token_query_dict, not both.")

        params = OrderedDict([
            ('sSessionKey', self.api.session_key),
            ('iSurveyID', survey_id),
            ('aTokenQueryProperties', token_query_dict),
            ('aTokenProperties', [])
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Error: Invalid survey ID",
                "Error: No token table",
                "Error: No results were found based on your attributes.",
                "Error: More than 1 result was found based on your attributes.",
                "Error: Invalid tokenid",
                "No valid Data",
                "No permission",
                "Invalid Session Key"
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)

        assert response_type is dict
        return response

    def invite_participants(self, survey_id, token_ids, uninvited_only=True):
        """
        Send invitation emails for the specified survey participants.

        Parameters
        :param survey_id: ID of survey to invite participants from.
        :type survey_id: Integer
        :param token_ids: List of token IDs for participants to invite.
        :type token_ids: List[Integer]
        :param uninvited_only: If True, only send emails for participants that
          have not been invited. If False, send an invite even if already sent.
        :type uninvited_only: Bool
        """
        method = "invite_participants"
        params = OrderedDict([
            ('sSessionKey', self.api.session_key),
            ('iSurveyID', survey_id),
            ('aTokenIDs', token_ids),
            ('bEmail', uninvited_only)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Invalid session key",
                "Error: Invalid survey ID",
                "Error: No token table",
                "Error: No candidate token_ids",
                "No permission",
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)

        assert response_type is dict
        return response

    def list_participants(self):
        # TODO
        raise NotImplementedError

    def get_summary(self):
        # TODO
        raise NotImplementedError
