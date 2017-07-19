import os
import unittest
from operator import itemgetter
from limesurveyrc2api.limesurveyrc2api import LimeSurveyRemoteControl2API
from configparser import ConfigParser


class TestBase(unittest.TestCase):

    def setUp(self):
        
        # Read config.ini file
        current_dir = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(current_dir, 'config.ini')
        confparser = ConfigParser()
        confparser.read_file(open(config_path))
        self.url = confparser['test']['url']
        self.username = confparser['test']['username']
        self.password = confparser['test']['password']
        self.api = LimeSurveyRemoteControl2API(self.url)
        self.session_key = None

    def tearDown(self):
        """
        Clean up any side effects.

        Tests should assign to self.session_key so this cleanup can occur.
        """
        if self.session_key is not None:
            self.api.sessions.release_session_key(self.session_key)


class TestSessions(TestBase):

    def test_get_session_key_success(self):
        """
        Requesting a session key with valid creds should return a session key.

        - A. Verify the return value for valid credentials is a 32 char string.
        """

        # A
        result = self.api.sessions.get_session_key(self.username, self.password)
        result_value = result.get('result')
        self.assertEqual(32, len(result_value))
        self.assertEqual(str, type(result_value))
        self.session_key = result_value

    def test_get_session_key_failure(self):
        """
        Requesting a session key with invalid creds should return None

        - A. Verify the return value for bad credentials is None
        """

        # A
        result = self.api.sessions.get_session_key('bad_user', 'bad_pass')
        result_value = result.get('result')
        result_status = result_value.get('status')
        self.assertEqual("Invalid user name or password", result_status)

    def test_release_session_key_success(self):
        """
        Releasing a valid session key should return "OK".

        - A. Get a session key.
        - B. Verify the return for a valid release request is "OK".
        - C. Verify the return for a call using the released key fails.
        """

        # A
        session = self.api.sessions.get_session_key(
            self.username, self.password)
        session_key = session.get('result')

        # B
        result = self.api.sessions.release_session_key(session_key)
        result_value = result.get('result')
        self.assertEqual("OK", result_value)

        # C
        call = self.api.surveys.list_surveys(result_value, self.username)
        call_value = call.get('result')
        call_status = call_value.get('status')
        self.assertEqual("Invalid session key", call_status)

    def test_release_session_key_failure(self):
        """
        Releasing an invalid session key should return "OK".

        - A. Verify the return for an invalid release request is "OK".
        """

        # A
        result = self.api.sessions.release_session_key("boguskey")
        result_value = result.get('result')
        self.assertEqual("OK", result_value)


class TestSurveys(TestBase):

    def test_list_surveys_success(self):
        """
        Requesting a list of surveys for a user should return survey properties.

        - A. Get a new session key.
        - B. Verify the result contains dict(s) each with a survey_id.
        """

        # A
        session = self.api.sessions.get_session_key(
            self.username, self.password)
        self.session_key = session.get('result')

        # B
        result = self.api.surveys.list_surveys(self.session_key, self.username)
        result_value = result.get('result')
        for survey in result_value:
            self.assertIsNotNone(survey.get('sid'))

    def test_list_surveys_failure(self):
        """
        Requesting a survey list for an invalid username should return error.

        - A. Get new session key.
        - B. Verify the result status is "Invalid user".
        """

        # A
        session = self.api.sessions.get_session_key(
            self.username, self.password)
        self.session_key = session.get('result')

        # B
        result = self.api.surveys.list_surveys(self.session_key, "not_a_user")
        result_value = result.get('result')
        status = result_value.get('status')
        self.assertEqual("Invalid user", status)


class TestTokens(TestBase):

    def test_add_participants_success(self):
        """
        Adding a participant to a survey should return their token string.

        - A. Get a new session key.
        - B. Get the survey id.
        - C. Add participants.
        - D. Verify the return for a valid request matches and has a token.
        """

        # A
        session = self.api.sessions.get_session_key(
            self.username, self.password)
        self.session_key = session.get('result')

        # B
        surveys = self.api.surveys.list_surveys(self.session_key, self.username)
        survey_id = surveys.get('result')[0].get('sid')

        # C
        participants = [
            {'email': 't1@test.com', 'lastname': 'LN1', 'firstname': 'FN1'},
            {'email': 't2@test.com', 'lastname': 'LN2', 'firstname': 'FN2'},
            {'email': 't3@test.com', 'lastname': 'LN3', 'firstname': 'FN3'},
        ]
        result = self.api.tokens.add_participants(
            self.session_key, survey_id, participants)

        # D
        result_value = result.get('result')
        tokens = sorted(result_value, key=itemgetter('tid'))
        zipped = zip(tokens, participants)
        for token, participant in zipped:
            for key in participant:
                self.assertEqual(participant[key], token[key])
                self.assertIsNotNone(token["token"])

    def test_add_participants_failure_survey(self):
        """
        Add participants to an invalid survey returns an error.

        - A. Get a new session key.
        - B. Add participants to an invalid survey id.
        - C. Verify the return for a invalid request is an error.
        """
        # A
        session = self.api.sessions.get_session_key(
            self.username, self.password)
        self.session_key = session.get('result')

        # B
        surveys = self.api.surveys.list_surveys(self.session_key, self.username)
        survey_ids = [s.get('sid') for s in surveys.get('result')]
        # construct an invalid survey ID by taking the longest ID (these are strings) and appending a '9'
        survey_id_invalid = sorted(survey_ids, key=len)[-1] + '9'

        participants = [
            {'email': 't1@test.com', 'lastname': 'LN1', 'firstname': 'FN1'},
            {'email': 't2@test.com', 'lastname': 'LN2', 'firstname': 'FN2'},
            {'email': 't3@test.com', 'lastname': 'LN3', 'firstname': 'FN3'},
        ]
        result = self.api.tokens.add_participants(
            self.session_key, survey_id_invalid, participants)

        # C
        result_value = result.get('result')
        status = result_value.get('status')
        self.assertEqual("Error: Invalid survey ID", status)

    def test_add_participants_success_anonymous(self):
        """
        Adding anonymous participants to an valid survey returns tokens.

        - A. Get a new session key.
        - B. Get valid survey ID.
        - C. Add anonymous participants to valid survey id.
        - D. Verify the return for a valid request matches and has a token.
        """
        # A
        session = self.api.sessions.get_session_key(
            self.username, self.password)
        self.session_key = session.get('result')

        # B
        surveys = self.api.surveys.list_surveys(self.session_key, self.username)
        survey_id = surveys.get('result')[0].get('sid')

        # C
        participants = [
            {'email': 't1@test.com'},
            {'lastname': 'LN2'},
            {'firstname': 'FN3'},
        ]
        result = self.api.tokens.add_participants(
            self.session_key, survey_id, participants)

        # D
        result_value = result.get('result')
        tokens = sorted(result_value, key=itemgetter('tid'))
        zipped = zip(tokens, participants)
        for token, participant in zipped:
            for key in participant:
                self.assertEqual(participant[key], token[key])
                self.assertIsNotNone(token["token"])

    def test_delete_participants_success(self):
        """
        Deleting participants should return deleted token id list.

        A. Get new session key.
        B. Get a valid survey ID.
        C. Create valid tokens.
        D. Verify the delete response is the list of token ids and "Deleted".
        """

        # A
        session = self.api.sessions.get_session_key(
            self.username, self.password)
        self.session_key = session.get('result')

        # B
        surveys = self.api.surveys.list_surveys(self.session_key, self.username)
        survey_id = surveys.get('result')[0].get('sid')

        # C
        participants = [
            {'email': 't1@test.com', 'lastname': 'LN1', 'firstname': 'FN1'},
            {'email': 't2@test.com', 'lastname': 'LN2', 'firstname': 'FN2'},
            {'email': 't3@test.com', 'lastname': 'LN3', 'firstname': 'FN3'},
        ]
        result = self.api.tokens.add_participants(
            self.session_key, survey_id, participants)

        # D
        result_value = result.get('result')
        token_ids = [x["tid"] for x in result_value]
        deleted = self.api.tokens.delete_participants(
            self.session_key, survey_id, token_ids)
        deleted_tokens = deleted.get('result')
        for token_id, token_result in deleted_tokens.items():
            self.assertIn(token_id, token_ids)
            self.assertEqual("Deleted", token_result)

    def test_delete_participants_failure(self):
        """
        Requesting to delete a token that doesn't exist returns an error.

        A. Get new session key.
        B. Get a valid survey ID.
        C. Verify the result of delete for non existent token id is an error.
        """
        # A
        session = self.api.sessions.get_session_key(
            self.username, self.password)
        self.session_key = session.get('result')

        # B
        surveys = self.api.surveys.list_surveys(self.session_key, self.username)
        survey_id = surveys.get('result')[0].get('sid')

        # C TODO: derive from list_participants() to ensure it won't be wrong
        tokens = [92929292, 929292945, 2055031111]
        result = self.api.tokens.delete_participants(
            self.session_key, survey_id, tokens)
        result_value = result.get('result')
        for token_id, token_result in result_value.items():
            self.assertIn(int(token_id), tokens)
            self.assertEqual("Invalid token ID", token_result)


class TestQuestions(TestBase):

    def test_list_questions_success(self):
        """
        Request to list questions for a valid survey should return the list.

        A. Get a new session key.
        B. Get a valid survey ID.
        C. Verify the result contains a list with the SGQA components.
        """
        # A
        session = self.api.sessions.get_session_key(
            self.username, self.password)
        self.session_key = session.get('result')

        # B
        surveys = self.api.surveys.list_surveys(self.session_key, self.username)
        survey_id = surveys.get('result')[0].get('sid')

        # C
        questions = self.api.questions.list_questions(
            self.session_key, survey_id)
        question_list = questions.get('result')
        self.assertIsInstance(question_list, list)
        for question in question_list:
            self.assertEqual(survey_id, question["sid"])
            self.assertIsNotNone(question["gid"])
            self.assertIsNotNone(question["qid"])

    def test_list_questions_failure(self):
        """
        Requesting a question list for an invalid survey id returns an error.

        A. Get a new session key.
        B. Verify the result for a question list request is an error.
        """

        # A
        session = self.api.sessions.get_session_key(
            self.username, self.password)
        self.session_key = session.get('result')

        # B TODO: derive from list_surveys() to ensure it won't be wrong
        survey_id = 9999999
        result = self.api.questions.list_questions(self.session_key, survey_id)
        result_value = result.get('result')
        status = result_value.get('status')
        self.assertEqual("Error: Invalid survey ID", status)
