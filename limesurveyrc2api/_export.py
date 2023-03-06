from collections import OrderedDict
from limesurveyrc2api.exceptions import LimeSurveyError


class _Export(object):

    def __init__(self, api):
        self.api = api

    def export_responses(self, survey_id, doc_type='csv', completion_status='all', response_type='short',
                         lang_code='de'):
        """
        Get all responses
        :param survey_id: ID of the survey
        :param doc_type: pdf, csv, xls, doc, json
        :param completion_status: complete, incomplete, all
        :param response_type: short or long
        :param lang_code: The language to be used
        :return: On success: Requested file as base 64-encoded string. On failure array with error information
        """
        method = "export_responses"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID", survey_id),
            ("sDocumentType", doc_type),
            ("sLanguageCode", lang_code),
            ("sCompletionStatus", completion_status),
            ("sHeadingType", "full"),
            ("sResponseType", response_type),
            # ("aFields", )
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Invalid user",
                "No surveys found",
                "Invalid session key",
                "No Data, survey table does not exist."
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)
        else:
            return response
