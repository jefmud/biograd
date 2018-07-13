from urllib.request import urlopen
from urllib.parse import urlencode
import json

# you could possibly put these in the settings file, these are app-secrets, but could possibly be encoded into a database table
qualtrics_url = ''
qualtrics_user = ''
qualtrics_token = ''

demog_survey_params = {
    'User': qualtrics_user,
    'Token': qualtrics_token,
    'SurveyID': '',
    'Version': '2.4',
    'Format': 'JSON',
    }

progress_survey_params = {
    'User': qualtrics_user,
    'Token': qualtrics_token,
    'SurveyID': '',
    'Version': '2.4',
    'Format': 'JSON',
    }

def get_qualtrics_JSON(url, params):
    """get_qualtrics_JSON(url, params) - gets the JSON data from a particular Qualtrics survey
    url = The Qualtrics API base URL
    params = Dictionary of User, Token, and SurveyID, Version, Format
    returns JSON array data
    """
    data = None
    enc_params = urlencode(params).encode("utf-8")
    try:
        request = urlopen(url, data=enc_params).read()
        data = json.loads(request)
    except Exception as e:
        print(e)

    return data
demo_params = {
}


# simply ask for qualtrics JSON from surveys (see above parameters)
def get_demog_JSON():
    return get_qualtrics_JSON(qualtrics_url, demog_survey_params)
def get_progress_JSON():
    return get_qualtrics_JSON(qualtrics_url, progress_survey_params)

if __name__ == '__main__':
    print("Test demography fetch")
    data = get_demog_JSON()
    print(data)
