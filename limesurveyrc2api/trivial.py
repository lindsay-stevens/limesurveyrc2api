from limesurveyrc2api import LimeSurveyRemoteControl2API

url = 'http://localhost:443/limesurvey/index.php/admin/remotecontrol'
username = 'admin'
password = 'admin'

api = LimeSurveyRemoteControl2API(url)
session_req = api.sessions.get_session_key(username, password)
session_key = session_req.get('result')
surveys_req = api.surveys.list_surveys(session_key, username)
surveys = surveys_req.get('result')
for survey in surveys:
    print(survey.get('sid'))
