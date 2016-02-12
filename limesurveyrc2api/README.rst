LimeSurvey RC2 API Web Services Client
======================================
This module provides a class which can be used as a client for interacting
with LimeSurvey Remote Control 2 API.


Example Usage
*************
The tests are a good place to refer to for api usage, until proper docs are
written, anyway. Here is how to get a list of surveys.

.. code-block:: python
    from limesurveyrc2api import LimeSurveyRemoteControl2API

    url = 'http://localhost:443/limesurvey/index.php/admin/remotecontrol'
    username = 'admin'
    password = 'admin'

    # Make a session.
    api = LimeSurveyRemoteControl2API(url)
    session_req = api.sessions.get_session_key(username, password)
    session_key = session_req.get('result')

    # Get a list of surveys the admin can see, and print their IDs.
    surveys_req = api.surveys.list_surveys(session_key, username)
    surveys = surveys_req.get('result')
    for survey in surveys:
        print(survey.get('sid'))


Implemented Methods
*******************
It's just a start, so the list of implemented methods is shorter than not.

- Sessions
  + get_session_key
  + release_session_key
- Surveys
  + list_surveys
- Tokens
  + add_participants
  + delete_participants
- Questions
  + list_questions


Running Tests
*************
- Edit the tests/config.ini with the details of a RC2API enabled LimeSurvey
  installation.
- Make sure there is at least 1 survey loaded in the installation (once the
  create survey method is implemented, that could be used instead).
- Run the tests.py script.
