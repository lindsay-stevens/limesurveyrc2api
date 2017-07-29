# LimeSurvey RC2 API Web Services Client


## Introduction
This module provides a class which can be used as a client for interacting with LimeSurvey Remote Control 2 API.


## Example Usage
The tests are a good place to refer to for api usage, until proper docs are written, anyway. Here is how to get a list of surveys.

```python
from limesurveyrc2api.limesurvey import LimeSurvey

url = 'http://localhost:443/limesurvey/index.php/admin/remotecontrol'
username = 'admin'
password = 'admin'

# Open a session.
api = LimeSurvey(url=url, username=username)
api.open(password=password)

# Get a list of surveys the admin can see, and print their IDs.
result = self.api.survey.list_surveys()
for survey in result:
    print(survey.get('sid'))

# Close the session.
api.close()
```

## Implemented Methods
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


## Running Tests
- Copy tests/config.ini.tmpl to tests/config.ini and edit it with the details of 
   a RC2API enabled LimeSurvey installation.
  - To enable, login as admin, go to Configuration -> Global Settings -> Interfaces -> RPC interface enabled: JSON-RPC -> Save
- Make sure there is at least 1 survey loaded in the installation (once the create survey method is implemented, that could be used instead).
- Run the tests.py script.


### Test Problems

There is a PHP 5.6.0+ issue where the API response value includes a deprecation warning, which breaks the JSON response parsing. To deal with this, ensure that the following `php.ini` setting is set: `always_populate_raw_post_data = -1`.