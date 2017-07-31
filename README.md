# LimeSurvey RC2 API Web Services Client


## Introduction

This module provides a class which can be used as a client for interacting with LimeSurvey Remote Control 2 API.


### Example Usage

The tests are a good place to refer to for api usage, until proper docs are written, anyway. Here is how to get a list of surveys.

```python
from limesurveyrc2api.limesurvey import LimeSurvey

url = "http://localhost:443/limesurvey/index.php/admin/remotecontrol"
username = "admin"
password = "admin"

# Open a session.
api = LimeSurvey(url=url, username=username)
api.open(password=password)

# Get a list of surveys the admin can see, and print their IDs.
result = self.api.survey.list_surveys()
for survey in result:
    print(survey.get("sid"))

# Close the session.
api.close()
```

### Implemented Methods

It's just a start, so the list of implemented methods is shorter than not.

- Sessions
  + get_session_key (api.open)
  + release_session_key (api.close)
- Survey
  + list_surveys
  + list_questions
- Token
  + add_participants
  + delete_participants
  + get_participant_properties
  + invite_participants


### Error Handling

Where possible, error messages from the RC2API are translated into Python exceptions (specifically, a `LimeSurveyError`), with the caller method and error message included in the exception message plus any other relevant info.



## Development


### References

Useful references for the RC2API:

- [Handler script](https://github.com/LimeSurvey/LimeSurvey/blob/master/application/helpers/remotecontrol/remotecontrol_handle.php)
- [Server script](https://github.com/LimeSurvey/LimeSurvey/blob/master/application/libraries/LSjsonRPCServer.php)
- [Manual page](https://manual.limesurvey.org/RemoteControl_2_API)
- [Generated api doc](https://api.limesurvey.org/classes/remotecontrol_handle.html)


### Discovering Error Messages

If extending or maintaining this project, be aware that discovering error messages to raise an exception from is a relatively tedious process. It involves reading through the handler script, looking for lines like the following.

```php
return array('status' => 'No permission');
```

Whether or not the message is an error depends on the context of the line and the message text. For example, some RC2API methods that delete objects return a message that looks like an error but indicate success, e.g. "status": "OK".


### Running Tests

- Copy tests/config.ini.tmpl to tests/config.ini and edit it with the details of a RC2API enabled LimeSurvey installation.
- LimeSurvey instance setup steps:
  - Install LimeSurvey by following the manual instructions
  - Log in as admin, then go to Configuration -> Global Settings:
    - Enable the RC2API, under: Interfaces -> RPC interface enabled: JSON-RPC -> Save
    - Configure the test smtp host, under Email settings:
      - Email method: SMTP
      - SMTP host: localhost:10025
      - SMTP username, password: blank
      - Email batch size: 50
      - Save
  - Load at least 1 survey, by either:
    - Logging in as admin, then Surveys -> Create a new survey, then add groups and questions by hand
    - Logging in as admin, then Surveys -> Create a new survey, then import the .LSS file under tests/fixtures
    - Once the methods are implemented for it, create a survey programmatically
  - Activate the survey: Surveys -> SurveyName -> Activate this Survey
  - Initialise participants table: Survey -> SurveyName -> Survey Participants -> Initialise participants table
- From the project root folder, run the tests either:
  - For minimal result info: `python -m unittest`
  - For more detailed info: `python setup.py test`


### Test Problems

There is a PHP 5.6.0+ issue where the API response value includes a deprecation warning, which breaks the JSON response parsing. To deal with this, ensure that the following `php.ini` setting is set: `always_populate_raw_post_data = -1`.


### Intellij Setup

Project setup for IDEA requires defining a "project SDK", under File -> Project Structure -> Project. Since this is a Python project, the SDK is the interpreter you want to use, which could (should) be a virtual environment interpreter.

Since the SDK setting is user specific, it'll need to be created the first time you load up this project. This should create an entry under Platform Settings -> Global Libraries; and a file /.idea/misc.xml, containing the name of the global library (SDK) selected for this project.
