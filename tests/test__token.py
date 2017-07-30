from tests.test_limesurvey import TestBase
from limesurveyrc2api.limesurvey import LimeSurveyError
from operator import itemgetter
from tests.utils import CapturingAiosmtpdServer


class TestTokens(TestBase):

    def setUp(self):
        super().setUp()

        surveys = self.api.survey.list_surveys()
        self.survey_id = surveys[0].get('sid')
        self.survey_id_invalid = TestBase.get_invalid_survey_id(surveys)
        self.participants = [
            {'email': 't1@example.com', 'lastname': 'LN1', 'firstname': 'FN1'},
            {'email': 't2@example.com', 'lastname': 'LN2', 'firstname': 'FN2'},
            {'email': 't3@example.com', 'lastname': 'LN3', 'firstname': 'FN3'},
        ]
        self.token_ids = None  # Assign to this for deletion in tearDown

    def tearDown(self):
        try:
            if self.token_ids is not None:
                self.api.token.delete_participants(
                    survey_id=self.survey_id, token_ids=self.token_ids)
        except LimeSurveyError:
            pass  # Deletion didn't work because none were created.
        except AssertionError:
            pass  # Passing None for tokens param -> empty list -> assert error.
        super().tearDown()

    def test_get_summary(self):
        """
        Get summary of a survey
        """
        surveys = self.api.survey.list_surveys()
        survey_id = surveys[0].get('sid')
        survey_summary = self.api.token.get_summary(survey_id)
        # example response:
        # {'token_count': '26', 'token_invalid': '0', 'token_sent': '0',
        #  'token_opted_out': '0', 'token_completed': '0'}
        self.assertIn('token_count', survey_summary)
        self.assertIsInstance(survey_summary['token_count'], str)
        self.assertIn('token_invalid', survey_summary)
        self.assertIsInstance(survey_summary['token_invalid'], str)
        self.assertIn('token_sent', survey_summary)
        self.assertIsInstance(survey_summary['token_sent'], str)
        self.assertIn('token_opted_out', survey_summary)
        self.assertIsInstance(survey_summary['token_opted_out'], str)
        self.assertIn('token_completed', survey_summary)
        self.assertIsInstance(survey_summary['token_completed'], str)

        # error cases
        # invalid summary
        with self.assertRaises(LimeSurveyError) as ctx:
            self.api.token.get_summary(TestBase.get_invalid_survey_id(surveys))
        self.assertIn('Invalid surveyid', ctx.exception.message)

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
        survey_id = self.survey_id_invalid

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
            survey_id=self.survey_id, token_ids=self.token_ids)
        for token_id, token_result in deleted.items():
            self.assertIn(token_id, self.token_ids)
            self.assertEqual("Deleted", token_result)

    def test_delete_participants_token_failure(self):
        """Deleting a token that doesn't exist should return an error."""
        # TODO: derive from list_participants() to ensure it won't be wrong
        tokens = [92929292, 929292945, 2055031111]

        result = self.api.token.delete_participants(
            survey_id=self.survey_id, token_ids=tokens)
        for token_id, token_result in result.items():
            self.assertIn(int(token_id), tokens)
            self.assertEqual("Invalid token ID", token_result)

    def test_get_participant_properties_success(self):
        """Querying for a unique token should return its properties."""
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=self.participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        token0 = added_tokens[0]
        participant0 = self.participants[0]
        token0_props = self.api.token.get_participant_properties(
            survey_id=self.survey_id, token_id=token0["tid"])
        self.assertEqual(participant0["email"], token0_props["email"])

    def test_get_participant_properties_duplicate_failure(self):
        """Querying on a property with >1 results should return an error."""
        self.participants.append(self.participants[0])
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=self.participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        token_query_properties = {"email": self.participants[0]["email"]}

        with self.assertRaises(LimeSurveyError) as lse:
            self.api.token.get_participant_properties(
                survey_id=self.survey_id, token_id=None,
                token_query_properties=token_query_properties)
        self.assertIn(
            "Error: More than 1 result was found based on your attributes.",
            lse.exception.message)

    def test_invite_participants_success(self):
        """Sending invites for survey participants should relay all invites."""
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=self.participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        with CapturingAiosmtpdServer() as cas:
            message_statuses = self.api.token.invite_participants(
                survey_id=self.survey_id, token_ids=self.token_ids,
                uninvited_only=True)
        self.assertEqual(len(self.participants), len(cas.messages))
        overall_status = message_statuses.pop("status")
        self.assertEqual("0 left to send", overall_status)
        for token_id, email_info in message_statuses.items():
            self.assertEqual("OK", email_info.get("status"))

    def test_invite_participants_tokens_failure(self):
        """Sending invites for non-existent tokens should return an error."""
        token_ids = [92929292, 929292945, 2055031111]

        with self.assertRaises(LimeSurveyError) as lse:
            self.api.token.invite_participants(
                survey_id=self.survey_id, token_ids=token_ids,
                uninvited_only=True)
        self.assertIn("Error: No candidate tokens", lse.exception.message)

    def test_invite_participants_uninvited_failure(self):
        """Re-sending invites with uninvited_only should return an error."""
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=self.participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        with CapturingAiosmtpdServer():
            self.api.token.invite_participants(
                survey_id=self.survey_id, token_ids=self.token_ids,
                uninvited_only=True)
        with self.assertRaises(LimeSurveyError) as lse:
            self.api.token.invite_participants(
                survey_id=self.survey_id, token_ids=self.token_ids,
                uninvited_only=True)
        self.assertIn("Error: No candidate tokens", lse.exception.message)

    def test_invite_participants_uninvited_success(self):
        """Re-sending invites with uninvited_only=False should not re-send."""
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=self.participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        with CapturingAiosmtpdServer():
            self.api.token.invite_participants(
                survey_id=self.survey_id, token_ids=self.token_ids,
                uninvited_only=True)
        with CapturingAiosmtpdServer() as cas:
            self.api.token.invite_participants(
                survey_id=self.survey_id, token_ids=self.token_ids,
                uninvited_only=False)
        self.assertEqual(len(self.participants), len(cas.messages))

    def test_list_participants_success(self):
        """Query for all participants should return added token ids."""
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=self.participants)
        self.token_ids = [int(x["tid"]) for x in added_tokens]

        result = self.api.token.list_participants(survey_id=self.survey_id)
        result_token_ids = [x["tid"] for x in result]
        self.assertListEqual(self.token_ids, result_token_ids)

    def test_list_participants_conditions_failure(self):
        """Querying with a condition matching none should result in an error."""
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=self.participants)
        self.token_ids = [int(x["tid"]) for x in added_tokens]

        with self.assertRaises(LimeSurveyError) as lse:
            self.api.token.list_participants(
                survey_id=self.survey_id, conditions={"email": "not_an_email"})
        self.assertIn("No survey participants found.", lse.exception.message)
