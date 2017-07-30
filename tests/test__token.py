from tests.test_limesurvey import TestBase
from limesurveyrc2api.limesurvey import LimeSurveyError
from operator import itemgetter


class TestTokens(TestBase):

    def setUp(self):
        super().setUp()

        surveys = self.api.survey.list_surveys()
        self.survey_id = surveys[0].get('sid')
        self.participants = [
            {'email': 't1@test.com', 'lastname': 'LN1', 'firstname': 'FN1'},
            {'email': 't2@test.com', 'lastname': 'LN2', 'firstname': 'FN2'},
            {'email': 't3@test.com', 'lastname': 'LN3', 'firstname': 'FN3'},
        ]
        self.token_ids = None  # Assign to this for deletion in tearDown

    def tearDown(self):
        try:
            self.api.token.delete_participants(
                survey_id=self.survey_id, tokens=self.token_ids)
        except LimeSurveyError:
            pass  # Deletion didn't work because none were created.
        except AssertionError:
            pass  # Passing None for tokens param -> empty list -> assert error.
        super().tearDown()

    def test_add_participants_success(self):
        """Adding participants to a survey should return their tokens."""
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=self.participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        tokens = sorted(added_tokens, key=itemgetter('tid'))
        zipped = zip(tokens, self.participants)
        for token, participant in zipped:
            for key in participant:
                self.assertEqual(participant[key], token[key])
                self.assertIsNotNone(token["token"])

    def test_add_participants_survey_failure(self):
        """Adding participants to an invalid survey should return an error."""
        survey_id = self.survey_id + 9

        with self.assertRaises(LimeSurveyError) as ctx:
            self.api.token.add_participants(
                    survey_id=survey_id, participant_data=self.participants)
        self.assertIn("Error: Invalid survey ID", ctx.exception.message)

    def test_delete_participants_success(self):
        """Deleting participants should return deleted token id list."""
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=self.participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        deleted = self.api.token.delete_participants(
            survey_id=self.survey_id, tokens=self.token_ids)
        for token_id, token_result in deleted.items():
            self.assertIn(token_id, self.token_ids)
            self.assertEqual("Deleted", token_result)

    def test_delete_participants_token_failure(self):
        """Deleting a token that doesn't exist should return an error."""
        # TODO: derive from list_participants() to ensure it won't be wrong
        tokens = [92929292, 929292945, 2055031111]

        result = self.api.token.delete_participants(
            survey_id=self.survey_id, tokens=tokens)
        for token_id, token_result in result.items():
            self.assertIn(int(token_id), tokens)
            self.assertEqual("Invalid token ID", token_result)

    def test_get_participant_properties_success(self):
        """Getting a token from a survey should return its properties."""
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=self.participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        token0 = added_tokens[0]
        participant0 = self.participants[0]
        token0_props = self.api.token.get_participant_properties(
            survey_id=self.survey_id, token_id=token0["tid"])
        self.assertEqual(participant0["email"], token0_props["email"])
