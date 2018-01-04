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

    def copy_survey(self, survey_id_org, new_name):
        # TODO: Make it work
        """ RCP Routine to copy a survey.
        
        Parameters
        :param survey_id_org: ID of the source survey.
        :type survey_id_org: Integer
        :param new_name: Name of the new survey.
        :type new_name: String
        """
        method = "copy_survey"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID_org", survey_id_org),
            ("sNewname", new_name)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Copy failed",
                "Invalid session key"
            ]
            for message in error_messages:
                if status == message:
                    # return response instead of status, because of own error
                    # message in case of "Copy failed" in response['error']
                    raise LimeSurveyError(method, response)
        else:
            assert response_type is list
        return response

    def import_survey(self, path_to_import_survey, new_name=None,
                      dest_survey_id=None):
        """ Import a survey. Allowed formats: lss, csv, txt or lsa
        
        Parameters
        :param path_to_import_survey: Path to survey as file to copy.
        :type path_to_import_survey: String
        :param new_name (optional): The optional new name of the survey
        :type new_name: String
        :param dest_survey_id (optional): This is the new ID of the survey - 
                          if already used a random one will be taken instead
        :type dest_survey_id: Integer
        """
        import_datatype = splitext(path_to_import_survey)[1][1:]
        with open(path_to_import_survey, 'rb') as f:
            # import data must be a base 64 encoded string
            import_data = b64encode(f.read())
            # decoding needed because json.dumps() in method get of
            # class LimeSurvey can not encode bytes
            import_data = import_data.decode('ascii')

        method = "import_survey"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("sImportData", import_data),
            ("sImportDataType", import_datatype),
            ("sNewSurveyName", new_name),
            ("DestSurveyID", dest_survey_id)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Error: ...",  # TODO: What might the error message of ImportResults be?
                "Invalid extension",
                "No permission",
                "Invalid session key"
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)
        else:
            assert response_type is int  # the new survey id
        return response
