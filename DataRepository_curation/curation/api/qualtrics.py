from os.path import join
from ..retrieve import private_file_retrieve
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

    def __init__(self, dataCenter, token, survey_id):
        self.apiToken = token
        self.dataCenter = dataCenter
        self.headers = {"X-API-TOKEN": self.apiToken,
                        "Content-Type": "application/json"}
        self.baseurl = "https://{0}.qualtrics.com/API/v3/".format(self.dataCenter)
        self.survey_id = survey_id
        self.fileFormat = 'csv'

    def list_surveys(self):
        url = join(self.baseurl, 'surveys')
        survey_list = issue_request('GET', url, headers=self.headers)

        return survey_list

    def get_survey_responses(self):
        progress_status = "inProgress"

        download_url = join(self.baseurl, "surveys/{0}/export-responses".format(self.survey_id))

        # Step 1: Creating Data Export
        download_payload = {"format": self.fileFormat}
        download_response = issue_request("POST", download_url, data=download_payload,
                                          headers=self.headers)
        progress_id = download_response["result"]["progressId"]

        # Step 2: Checking on Data Export Progress and waiting until export is ready
        while progress_status != "complete" and progress_status != "failed":
            print("progress_status: {}".format(progress_status))
            check_url = join(download_url, progress_id)
            check_response = issue_request("GET", check_url, headers=self.headers)
            check_progress = check_response["result"]["percentComplete"]
            print("Download is " + str(check_progress) + " complete")
            progress_status = check_response["result"]["status"]

        # step 2.1: Check for error
        if progress_status is "failed":
            raise Exception("export failed")

        file_id = check_response["result"]["fileId"]

        # Step 3: Downloading file
        download_url = join(download_url, '{0}/file'.format(file_id))
        print(download_url)
        # private_file_retrieve(download_url, filename='qualtrics.csv', token=self.apiToken)
        # print('Complete')
