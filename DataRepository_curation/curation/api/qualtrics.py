from os.path import join
import configparser
import requests
import pandas as pd

import zipfile
import io
from os import remove

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
      A Python interface for interaction with Qualtrics API for Deposit Agreement form survey

    Attributes
    ----------
    token : str
      The Qualtrics API Key authentication token

    data_center : str
      Qualtrics Data Center prefix

    baseurl : str
      Base URL of the Qualtrics v3 API

    headers : dict
      HTTP header information

    survey_id : str
      Qualtrics survey ID, begins as SV_*

    file_format : str
      Type of format for export response.  Using CSV

    Methods
    -------
    list_surveys()
      List all surveys for a user:
      See: https://api.qualtrics.com/docs/managing-surveys#list-surveys

    get_survey_responses()
      Retrieve pandas DataFrame containing responses from survey
      See: https://api.qualtrics.com/docs/getting-survey-responses-via-the-new-export-apis
    """

    def __init__(self, dataCenter, token, survey_id):
        self.token = token
        self.data_center = dataCenter
        self.baseurl = "https://{0}.qualtrics.com/API/v3/".format(self.data_center)
        self.headers = {"X-API-TOKEN": self.token,
                        "Content-Type": "application/json"}
        self.survey_id = survey_id
        self.file_format = 'csv'

    def endpoint(self, link):
        """Concatenate the endpoint to the baseurl"""
        return join(self.baseurl, link)

    def list_surveys(self):
        url = self.endpoint('surveys')
        survey_list = issue_request('GET', url, headers=self.headers)

        return survey_list

    def get_survey_responses(self):
        progress_status = "inProgress"

        download_url = self.endpoint("surveys/{0}/export-responses".format(self.survey_id))

        # Create Data Export
        download_payload = {"format": self.file_format}
        download_response = issue_request("POST", download_url, data=download_payload,
                                          headers=self.headers)
        progress_id = download_response["result"]["progressId"]

        # Check on Data Export Progress and waiting until export is ready
        while progress_status != "complete" and progress_status != "failed":
            print("progress_status: {}".format(progress_status))
            check_url = join(download_url, progress_id)
            check_response = issue_request("GET", check_url, headers=self.headers)
            check_progress = check_response["result"]["percentComplete"]
            print("Download is " + str(check_progress) + " complete")
            progress_status = check_response["result"]["status"]

        # Check for error
        if progress_status is "failed":
            raise Exception("export failed")

        file_id = check_response["result"]["fileId"]

        # Retrieve zipfile and extract and read in CSV into pandas DataFrame
        download_url = join(download_url, '{0}/file'.format(file_id))
        requestDownload = requests.request("GET", download_url, headers=self.headers, stream=True)
        input_zip = zipfile.ZipFile(io.BytesIO(requestDownload.content))
        csv_filename = input_zip.namelist()[0]
        input_zip.extract(csv_filename)

        response_df = pd.read_csv(csv_filename)
        remove(csv_filename)

        return response_df
