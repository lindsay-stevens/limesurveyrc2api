from tests.test_limesurvey import TestBase
from limesurveyrc2api.limesurvey import LimeSurveyError
from operator import itemgetter
from tests.utils import CapturingAiosmtpdServer


class TestTokens(TestBase):
    """Tests that create, modify, or delete tokens."""

    token_ids = None
    participants = [
        {"email": "t1@example.com", "firstname": "FN1"},
        {"email": "t2@example.com", "firstname": "FN2"},
        {"email": "t3@example.com", "firstname": "FN3"}]

    def tearDown(self):
        try:
            self.api.token.delete_participants(
                survey_id=self.survey_id, token_ids=self.token_ids)
        except LimeSurveyError:
            pass  # Deletion didn't work because none were created.
        except AssertionError:
            pass  # Passing None for tokens param -> empty list -> assert error.

    def get_participants(self, method_name):
        participants = self.participants.copy()
        for participant in participants:
            participant.update({"lastname": method_name})
        return participants

    def test_add_participants_survey_failure(self):
        """Adding participants to an invalid survey should return an error."""
        participants = self.get_participants(
            "test_add_participants_survey_failure")

        with self.assertRaises(LimeSurveyError) as ctx:
            self.api.token.add_participants(
                survey_id=self.survey_id_invalid,
                participant_data=participants)
        self.assertIn("Error: Invalid survey ID", ctx.exception.message)

    def test_add_participants_success(self):
        """Adding participants to a survey should return their tokens."""
        participants = self.get_participants(
            "test_add_participants_success")
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        sorted_tokens = sorted(added_tokens, key=itemgetter('tid'))
        zipped = zip(sorted_tokens, participants)
        for token, participant in zipped:
            for key in participant:
                self.assertEqual(participant[key], token[key])
                self.assertIsNotNone(token["token"])

    def test_delete_participants_success(self):
        """Deleting participants should return deleted token id list."""
        participants = self.get_participants(
            "test_delete_participants_success")
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        deleted = self.api.token.delete_participants(
            survey_id=self.survey_id, token_ids=self.token_ids)
        for token_id, token_result in deleted.items():
            self.assertIn(token_id, self.token_ids)
            self.assertEqual("Deleted", token_result)

    def test_get_participant_properties_duplicate_failure(self):
        """Querying on a property with >1 results should return an error."""
        participants = self.get_participants(
            "test_get_participant_properties_duplicate_failure")
        participants.append(participants[0])
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        token_query_properties = {"email": participants[0]["email"]}

        with self.assertRaises(LimeSurveyError) as lse:
            self.api.token.get_participant_properties(
                survey_id=self.survey_id, token_id=None,
                token_query_properties=token_query_properties)
        self.assertIn(
            "Error: More than 1 result was found based on your attributes.",
            lse.exception.message)

    def test_invite_participants_success(self):
        """Sending invites for survey participants should relay all invites."""
        participants = self.get_participants(
            "test_invite_participants_success")
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        with CapturingAiosmtpdServer() as cas:
            message_statuses = self.api.token.invite_participants(
                survey_id=self.survey_id, token_ids=self.token_ids,
                uninvited_only=True)
        self.assertEqual(len(participants), len(cas.messages))
        overall_status = message_statuses.pop("status")
        self.assertEqual("0 left to send", overall_status)
        for token_id, email_info in message_statuses.items():
            self.assertEqual("OK", email_info.get("status"))

    def test_invite_participants_uninvited_failure(self):
        """Re-sending invites with uninvited_only should return an error."""
        participants = self.get_participants(
            "test_invite_participants_uninvited_failure")
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=participants)
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
        participants = self.get_participants(
            "test_invite_participants_uninvited_success")
        added_tokens = self.api.token.add_participants(
            survey_id=self.survey_id, participant_data=participants)
        self.token_ids = [x["tid"] for x in added_tokens]

        with CapturingAiosmtpdServer():
            self.api.token.invite_participants(
                survey_id=self.survey_id, token_ids=self.token_ids,
                uninvited_only=True)
        with CapturingAiosmtpdServer() as cas:
            self.api.token.invite_participants(
                survey_id=self.survey_id, token_ids=self.token_ids,
                uninvited_only=False)
        self.assertEqual(len(participants), len(cas.messages))


class TestTokensWithExisting(TestBase):
    """Tests that require tokens to exist but don't modify them in any way."""

    token_ids = None
    participants = [
            {"email": "t1@example.com", "firstname": "FN1"},
            {"email": "t2@example.com", "firstname": "FN2"},
            {"email": "t3@example.com", "firstname": "FN3"}]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for participant in cls.participants:
            participant.update({"lastname": "TestTokensWithExisting"})
        cls.added_tokens = cls.api.token.add_participants(
            survey_id=cls.survey_id, participant_data=cls.participants)
        cls.token_ids = [x["tid"] for x in cls.added_tokens]
        cls.api.token.invite_participants(survey_id=cls.survey_id,
                                          token_ids=cls.token_ids)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.api.token.delete_participants(
                survey_id=cls.survey_id, token_ids=cls.token_ids)
        except LimeSurveyError:
            pass  # Deletion didn't work because none were created.
        except AssertionError:
            pass  # Passing None for tokens param -> empty list -> assert error.

    def test_delete_participants_token_failure(self):
        """Deleting a token that doesn't exist should return an error."""
        # TODO: derive from list_participants() to ensure it won't be wrong
        tokens = [92929292, 929292945, 2055031111]

        result = self.api.token.delete_participants(
            survey_id=self.survey_id, token_ids=tokens)
        for token_id, token_result in result.items():
            self.assertIn(int(token_id), tokens)
            self.assertEqual("Invalid token ID", token_result)

    def test_get_summary_survey_failure(self):
        """Querying a survey that doesn't exist should return an error."""
        with self.assertRaises(LimeSurveyError) as ctx:
            self.api.token.get_summary(survey_id=self.survey_id_invalid)
        self.assertIn('Invalid surveyid', ctx.exception.message)

    def test_get_summary_stat_name_failure(self):
        """Querying a stat name that doesn't exist should return an error."""
        with self.assertRaises(LimeSurveyError) as ctx:
            self.api.token.get_summary(
                survey_id=self.survey_id,
                stat_name="airspeed velocity of an unladen swallow")
        self.assertIn('Invalid summary key', ctx.exception.message)

    def test_get_summary_count_success(self):
        """Querying a survey for a token count should return accurate result."""
        result = self.api.token.get_summary(survey_id=self.survey_id)
        self.assertEqual(len(self.participants), int(result["token_count"]))

    def test_get_summary_return_type_success(self):
        """Querying a survey should return stats with expected types."""
        result = self.api.token.get_summary(survey_id=self.survey_id)
        return_types = [
            ("token_count", str),
            ("token_invalid", str),
            ("token_sent", str),
            ("token_opted_out", str),
            ("token_completed", str),
        ]
        for key, value_type in return_types:
            self.assertIn(key, result)
            self.assertIsInstance(result[key], value_type)

    def test_get_participant_properties_success(self):
        """Querying for a unique token should return its properties."""
        token0 = self.added_tokens[0]
        participant0 = self.participants[0]
        token0_props = self.api.token.get_participant_properties(
            survey_id=self.survey_id, token_id=token0["tid"])
        self.assertEqual(participant0["email"], token0_props["email"])

    def test_invite_participants_tokens_failure(self):
        """Sending invites for non-existent tokens should return an error."""
        token_ids = [92929292, 929292945, 2055031111]

        with self.assertRaises(LimeSurveyError) as lse:
            self.api.token.invite_participants(
                survey_id=self.survey_id, token_ids=token_ids,
                uninvited_only=True)
        self.assertIn("Error: No candidate tokens", lse.exception.message)

    def test_list_participants_return_type_success(self):
        """Querying for participants should return attrs with expected types."""
        result = self.api.token.list_participants(survey_id=self.survey_id)[0]
        return_types_top = [
            ("tid", str),
            ("token", str),
            ("participant_info", dict),
        ]

        for key, value_type in return_types_top:
            self.assertIn(key, result, msg=key)
            self.assertIsInstance(result[key], value_type, msg=key)

        participant_info = result["participant_info"]
        return_types_pinfo = [
            ("firstname", str),
            ("lastname", str),
            ("email", str)
        ]
        for key, value_type in return_types_pinfo:
            self.assertIn(key, participant_info, msg=key)
            self.assertIsInstance(participant_info[key], value_type, msg=key)

    def test_list_participants_attribute_success(self):
        """Querying for a specific participant attr should return it."""
        default = self.api.token.list_participants(survey_id=self.survey_id)[0]
        self.assertNotIn('language', default)  # by default no extra attr
        result = self.api.token.list_participants(
            survey_id=self.survey_id, attributes=["language"])[0]
        self.assertIn('language', result)  # now we have 'language'

    def test_list_participants_conditions_success(self):
        """Querying with conditions should filter participant results."""
        participant = self.participants[0]
        result = self.api.token.list_participants(
            survey_id=self.survey_id,
            conditions={'email': participant['email']})
        self.assertEqual(1, len(result))

    def test_list_participants_survey_failure(self):
        """Querying for an invalid survey should return an error."""
        with self.assertRaises(LimeSurveyError) as ctx:
            self.api.token.list_participants(survey_id=self.survey_id_invalid)
        self.assertIn('Invalid survey ID', ctx.exception.message)

    def test_list_participants_success(self):
        """Query for all participants should return added token ids."""
        result = self.api.token.list_participants(survey_id=self.survey_id)
        result_token_ids = [x["tid"] for x in result]
        for token_id in self.token_ids:
            self.assertIn(token_id, result_token_ids)

    def test_list_participants_conditions_failure(self):
        """Querying with a condition matching none should result in an error."""
        with self.assertRaises(LimeSurveyError) as lse:
            self.api.token.list_participants(
                survey_id=self.survey_id, conditions={"email": "not_an_email"})
        self.assertIn("No survey participants found.", lse.exception.message)

    def test_remind_participants_success(self):
        """ Should return array of result of each email send action and a
        count of invitations left to send in status key. """
        with CapturingAiosmtpdServer() as cas:
            result = self.api.token.remind_participants(
                survey_id=self.survey_id)
        overall_status = result.pop("status")
        self.assertEqual("0 left to send", overall_status)
        for token_id, email_info in result.items():
            self.assertEqual("OK", email_info.get("status"))
            # TODO: cas.messages is [] here too...

    def test_remind_participants_success_individual_token(self):
        """ If token_ids is specified only remind those tokens. """
        remind_tokens = self.token_ids[:1]
        with CapturingAiosmtpdServer() as cas:
            result = self.api.token.remind_participants(
                self.survey_id, token_ids=remind_tokens)
        self.assertEqual(len(result), 2)  # token and general status
        self.assertIn(remind_tokens[0], result)

    def test_remind_participants_failure_min_days_between(self):
        """ Only remind participants if min days between last reminder. """
        with CapturingAiosmtpdServer():
            self.api.token.remind_participants(self.survey_id)
        with self.assertRaises(LimeSurveyError) as lse:
            self.api.token.remind_participants(
                survey_id=self.survey_id, min_days_between=1)
        self.assertIn("Error: No candidate tokens", lse.exception.message)

    def test_remind_participants_failure_max_reminders_count(self):
        """ Only remind participants if min days between last reminder. """
        with CapturingAiosmtpdServer():
            self.api.token.remind_participants(self.survey_id)
        with self.assertRaises(LimeSurveyError) as lse:
            self.api.token.remind_participants(
                survey_id=self.survey_id, max_reminders=1)
        self.assertIn("Error: No candidate tokens", lse.exception.message)
