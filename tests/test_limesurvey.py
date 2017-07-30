import os
import unittest
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

    @staticmethod
    def get_invalid_survey_id(surveys):
        """
        Determine a survey ID that does not exist in the list of surveys.

        :param surveys: existing surveys
        :type surveys: List[Dict]
        :return: invalid survey ID
        """
        survey_ids = [s.get('sid') for s in surveys]
        # construct an invalid survey ID by taking the longest ID
        # (these are strings) and appending a '9'
        return sorted(survey_ids, key=len)[-1] + '9'


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
