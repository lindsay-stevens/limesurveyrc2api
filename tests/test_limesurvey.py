import os
import unittest
from limesurveyrc2api.limesurvey import LimeSurvey, LimeSurveyError
from configparser import ConfigParser
from operator import itemgetter


class TestBase(unittest.TestCase):

    api = None
    survey_id = None
    participants = None

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
        cls.api.open(password=cls.password)
        if not confparser['test']['survey_id']:
            surveys = sorted(cls.api.survey.list_surveys(),
                             key=itemgetter("sid"))
            cls.survey_id = surveys[0].get("sid")
        else:
            cls.survey_id = confparser['test']['survey_id']
        cls.survey_id_invalid = -1

    @classmethod
    def tearDownClass(cls):
        try:
            cls.api.close()
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
