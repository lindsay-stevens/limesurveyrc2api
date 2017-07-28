import os
import unittest
from operator import itemgetter
from limesurveyrc2api.limesurvey import LimeSurvey, LimeSurveyError
from configparser import ConfigParser


class TestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        
        # Read config.ini file
        current_dir = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(current_dir, 'config.ini')
        confparser = ConfigParser()
        with open(config_path, "r") as config_file:
            confparser.read_file(config_file)
        cls.url = confparser['test']['url']
        cls.username = confparser['test']['username']
        cls.password = confparser['test']['password']
        cls.api = LimeSurvey(
            url=cls.url,
            username=cls.username)
        cls.session_key = None

    def setUp(self):
        self.api.open(password=self.password)

    def tearDown(self):
        try:
            self.api.close()
        except LimeSurveyError:
            pass


class TestSessionsNoSetup(TestBase):

    def setUp(self):
        """Test requires specifically opening a session so nullify default."""
        pass

    def test_get_session_key_failure(self):
        """Opening a session with invalid creds should raise an error."""
        with self.assertRaises(LimeSurveyError) as ctx:
            self.api.open(password=self.password + '_bad')
        self.assertIn('Invalid user name or password', ctx.exception.message)


class TestSessions(TestBase):

    def test_get_session_key_success(self):
        """Opening a session with valid creds should return a session key."""
        self.assertEqual(32, len(self.api.session_key))

    def test_release_session_key_success(self):
        """Releasing a valid session key should return "OK"."""
        result = self.api.close()
        self.assertEqual("OK", result)

    def test_release_session_key_failure(self):
        """Releasing an invalid session key should return "OK"."""
        real_key = self.api.session_key

        self.api.session_key = "boguskey"
        result = self.api.close()
        self.assertEqual("OK", result)

        self.api.session_key = real_key


class TestSurveys(TestBase):

    def test_list_surveys_success(self):
        """A valid request for list of surveys should not return empty."""
        result = self.api.survey.list_surveys()
        for survey in result:
            self.assertIsNotNone(survey.get('sid'))

    def test_list_surveys_failure(self):
        """An invalid request for list of surveys should raise an error."""
        with self.assertRaises(LimeSurveyError) as ctx:
            self.api.survey.list_surveys(username="not_a_user")
        self.assertIn("Invalid user", ctx.exception.message)


class TestTokens(TestBase):

    def test_add_participants_success(self):
        """Adding participants to a survey should return their tokens."""
        surveys = self.api.survey.list_surveys()
        survey_id = surveys[0].get('sid')
        participants = [
            {'email': 't1@test.com', 'lastname': 'LN1', 'firstname': 'FN1'},
            {'email': 't2@test.com', 'lastname': 'LN2', 'firstname': 'FN2'},
            {'email': 't3@test.com', 'lastname': 'LN3', 'firstname': 'FN3'},
        ]
        result = self.api.token.add_participants(survey_id, participants)
        tokens = sorted(result, key=itemgetter('tid'))
        zipped = zip(tokens, participants)
        for token, participant in zipped:
            for key in participant:
                self.assertEqual(participant[key], token[key])
                self.assertIsNotNone(token["token"])

        token_ids = [x["tid"] for x in result]
        self.api.token.delete_participants(survey_id, token_ids)

    def test_add_participants_failure_survey(self):
        """Adding participants to an invalid survey should return an error."""
        # A
        surveys = self.api.survey.list_surveys()
        survey_id = surveys[0].get('sid') + 9
        participants = [
            {'email': 't1@test.com', 'lastname': 'LN1', 'firstname': 'FN1'},
            {'email': 't2@test.com', 'lastname': 'LN2', 'firstname': 'FN2'},
            {'email': 't3@test.com', 'lastname': 'LN3', 'firstname': 'FN3'},
        ]
        with self.assertRaises(LimeSurveyError) as ctx:
            self.api.token.add_participants(survey_id, participants)
        self.assertIn("Error: Invalid survey ID", ctx.exception.message)

    def test_add_participants_success_anonymous(self):
        """Adding anon participants to a survey should return their tokens."""
        surveys = self.api.survey.list_surveys()
        survey_id = surveys[0].get('sid')
        participants = [
            {'email': 't1@test.com'},
            {'lastname': 'LN2'},
            {'firstname': 'FN3'},
        ]
        result = self.api.token.add_participants(survey_id, participants)
        tokens = sorted(result, key=itemgetter('tid'))
        zipped = zip(tokens, participants)
        for token, participant in zipped:
            for key in participant:
                self.assertEqual(participant[key], token[key])
                self.assertIsNotNone(token["token"])

        token_ids = [x["tid"] for x in result]
        self.api.token.delete_participants(survey_id, token_ids)

    def test_delete_participants_success(self):
        """Deleting participants should return deleted token id list."""
        surveys = self.api.survey.list_surveys()
        survey_id = surveys[0].get('sid')
        participants = [
            {'email': 't1@test.com', 'lastname': 'LN1', 'firstname': 'FN1'},
            {'email': 't2@test.com', 'lastname': 'LN2', 'firstname': 'FN2'},
            {'email': 't3@test.com', 'lastname': 'LN3', 'firstname': 'FN3'},
        ]
        result = self.api.token.add_participants(survey_id, participants)

        token_ids = [x["tid"] for x in result]
        deleted = self.api.token.delete_participants(survey_id, token_ids)
        for token_id, token_result in deleted.items():
            self.assertIn(token_id, token_ids)
            self.assertEqual("Deleted", token_result)

    def test_delete_participants_failure(self):
        """Deleting a token that doesn't exist should return an error."""
        surveys = self.api.survey.list_surveys()
        survey_id = surveys[0].get('sid')

        # TODO: derive from list_participants() to ensure it won't be wrong
        tokens = [92929292, 929292945, 2055031111]
        result = self.api.token.delete_participants(survey_id, tokens)
        for token_id, token_result in result.items():
            self.assertIn(int(token_id), tokens)
            self.assertEqual("Invalid token ID", token_result)

    def test_get_participant_properties_success(self):
        """Getting a token from a survey should return its properties."""
        surveys = self.api.survey.list_surveys()
        survey_id = surveys[0].get('sid')
        token = [
            {'email': 't1@test.com', 'lastname': 'LN1', 'firstname': 'FN1'},
        ]
        added_token = self.api.token.add_participants(survey_id, token)
        token_id = added_token[0]["tid"]
        result = self.api.token.get_participant_properties(survey_id, token_id)

        self.assertEqual(token[0]["email"], result["email"])

        self.api.token.delete_participants(survey_id, [token_id])


class TestQuestions(TestBase):

    def test_list_questions_success(self):
        """Listing questions for a survey should return a question list."""
        surveys = self.api.survey.list_surveys()
        survey_id = surveys[0].get('sid')

        result = self.api.survey.list_questions(survey_id)
        for question in result:
            self.assertEqual(survey_id, question["sid"])
            self.assertIsNotNone(question["gid"])
            self.assertIsNotNone(question["qid"])

    def test_list_questions_failure(self):
        """Listing questions for an invalid survey should returns an error."""
        surveys = self.api.survey.list_surveys()
        survey_id = surveys[0].get('sid') + 9
        with self.assertRaises(LimeSurveyError) as ctx:
            self.api.survey.list_questions(survey_id)
        self.assertIn("Error: Invalid survey ID", ctx.exception.message)
