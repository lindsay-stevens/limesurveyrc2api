import warnings
from collections import OrderedDict
from limesurveyrc2api.exceptions import LimeSurveyError
from os.path import splitext
from base64 import b64encode

class _Survey(object):

    def __init__(self, api):
        self.api = api

    def list_surveys(self, username=None):
        """
        List surveys accessible to the specified username.

        Parameters
        :param username: LimeSurvey username to list accessible surveys for.
        :type username: String
        """
        method = "list_surveys"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID", username or self.api.username)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Invalid user",
                "No surveys found",
                "Invalid session key"
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)
        else:
            assert response_type is list
        return response

    def list_questions(self, survey_id,
                       group_id=None, language=None):
        """
        Return a list of questions from the specified survey.

        Parameters
        :param survey_id: ID of survey to list questions from.
        :type survey_id: Integer
        :param group_id: ID of the question group to filter on.
        :type group_id: Integer
        :param language: Language of survey to return for.
        :type language: String
        """
        method = "list_questions"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID", survey_id),
            ("iGroupID", group_id),
            ("sLanguage", language)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Error: Invalid survey ID",
                "Error: Invalid language",
                "Error: IMissmatch in surveyid and groupid",
                "No questions found",
                "No permission",
                "Invalid session key"
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)
        else:
            assert response_type is list
        return response

    def export_responses(self, survey_id, document_type, language_code=None,
                         completion_status='all', heading_type='code',
                         response_type='short', from_response_id=None,
                         to_response_id=None, fields=None):
        """ Export responses in base64 encoded string.
        
        Parameters
        :param survey_id: Id of the Survey.
        :type survey_id: Integer
        :param document_type: Any format available by plugins 
                             (e.g. pdf, csv, xls, doc, json)
        :type document_type: String
        :param language_code: (optional) The language to be used.
        :type language_code: String
        :param completion_status: (optional) 'complete', 'incomplete' or 'all'
        :type completion_status: String
        :param heading_type: (optional) 'code', 'full' or 'abbreviated'
        :type heading_type: String
        :param response_type: (optional) 'short' or 'long'
        :type response_type: String
        :param from_response_id: (optional)
        :type from_response_id: Integer
        :param to_response_id: (optional)
        :type to_response_id: Integer
        :param fields: (optional) Selected fields.
        :type fields: Array
        """
        method = "export_responses"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID", survey_id),
            ("sDocumentType", document_type),
            ("sLanguageCode", language_code),
            ("sCompletionStatus", completion_status),
            ("sHeadingType", heading_type),
            ("sResponseType", response_type),
            ("iFromResponseID", from_response_id),
            ("iToResponseID", to_response_id),
            ("aFields", fields)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Language code not found for this survey.",
                "No Data, could not get max id.",
                "No Data, survey table does not exist",
                "No permission",
                "Invalid session key"
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)
        else:
            assert response_type is str
        return response
