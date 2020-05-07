from os.path import join
import requests

import configparser

from figshare.figshare import issue_request

# Read in default configuration file
config = configparser.ConfigParser()
config.read('DataRepository_curation/config/default.ini')

qualtrics_survey_id = config.get('curation', 'qualtrics_survey_id')
qualtrics_token = config.get('curation', 'qualtrics_token')
qualtrics_dataCenter = config.get('curation', 'qualtrics_dataCenter')


class QualtricsAPI:
    """
    Purpose:
      Retrieve data from Qualtrics survey
    """

    def __init__(self, dataCenter, token):
        self.apiToken = token
        self.dataCenter = dataCenter
        self.headers = {"X-API-TOKEN": self.apiToken,
                        "Content-Type": "application/json"}
        self.baseurl = "https://{0}.qualtrics.com/API/v3/".format(self.dataCenter)

    def list_surveys(self):
        url = join(self.baseurl, 'surveys')
        survey_list = issue_request('GET', url, headers=self.headers)

        return survey_list
