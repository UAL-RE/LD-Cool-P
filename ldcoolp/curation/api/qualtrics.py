from os.path import join
import io
from os import remove

# CSV handling
import zipfile
import pandas as pd

# URL handling
import requests
import json
from urllib.parse import quote, urlencode
import webbrowser

# Convert single-entry DataFrame to dictionary
from ldcoolp.curation import df_to_dict_single

# Logging
from ldcoolp.logger import log_stdout

# API
from figshare.figshare import issue_request

# Read in default configuration settings
from ...config import qualtrics_download_url, qualtrics_generate_url

# for quote and urlencode
url_safe = '/ {},:"?=@%'

# Column order for markdown print-out of Qualtrics table
cols_order = ['ResponseId', 'Q4_1', 'Q5', 'Q6_1', 'Q7']


class Qualtrics:
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
      List all surveys for a user in a dictionary form:
      See: https://api.qualtrics.com/docs/managing-surveys#list-surveys

    get_survey_responses()
      Retrieve pandas DataFrame containing responses for a survey
      See: https://api.qualtrics.com/docs/getting-survey-responses-via-the-new-export-apis

    find_deposit_agreement(dn_dict)
      Call get_survey_responses() and identify response that matches based on
      depositor name (implemented) and deposit title (to be implemented).
      Returns ResponseID if a unique match is available

    retrieve_deposit_agreement(dn_dict=, ResponseId=, browser=True)
      Opens up web browser to an HTML page containing the deposit agreement.
      It will call find_deposit_agreement() with DepositorName dict if
      ResponseId is not provided. Otherwise, it will use the provided
      ResponseId. Note that either dn_dict or ResponseId must be provided

    generate_url(dn_dict)
      Generate URL with customized query strings based on Figshare metadata
    """

    def __init__(self, dataCenter, token, survey_id, log=None):
        self.token = token
        self.data_center = dataCenter
        self.baseurl = "https://{0}.qualtrics.com/API/v3/".format(self.data_center)
        self.headers = {"X-API-TOKEN": self.token,
                        "Content-Type": "application/json"}
        self.survey_id = survey_id
        self.file_format = 'csv'

        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
            self.log = log

    def endpoint(self, link):
        """Concatenate the endpoint to the baseurl"""

        return join(self.baseurl, link)

    def list_surveys(self):
        """Return dictionary containing all surveys for a user"""

        url = self.endpoint('surveys')
        survey_dict = issue_request('GET', url, headers=self.headers)

        return survey_dict

    def get_survey_responses(self, verbose=False):
        """Retrieve pandas DataFrame containing responses for a survey"""

        progress_status = "inProgress"

        download_url = self.endpoint("surveys/{0}/export-responses".format(self.survey_id))

        # Create Data Export
        download_payload = {"format": self.file_format}
        download_response = issue_request("POST", download_url, data=download_payload,
                                          headers=self.headers)
        progress_id = download_response["result"]["progressId"]

        # Check on Data Export Progress and waiting until export is ready
        while progress_status != "complete" and progress_status != "failed":
            if verbose:
                self.log.debug("progress_status: {}".format(progress_status))
            check_url = join(download_url, progress_id)
            check_response = issue_request("GET", check_url, headers=self.headers)
            check_progress = check_response["result"]["percentComplete"]
            if verbose:
                self.log.debug("Download is " + str(check_progress) + " complete")
            progress_status = check_response["result"]["status"]

        # Check for error
        if progress_status is "failed":
            err = "export failed"
            self.log.warn(err)
            raise Exception(err)

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

    def find_deposit_agreement(self, dn_dict):
        """Get Response ID based on a match search for depositor name"""

        qualtrics_df = self.get_survey_responses()

        # First perform search via article_id or curation_id
        self.log.info("Attempting to identify using article_id or curation_id ...")
        article_id = str(dn_dict['article_id'])
        curation_id = str(dn_dict['curation_id'])

        try:
            response_df = qualtrics_df[(qualtrics_df['article_id'] == article_id) |
                                       (qualtrics_df['curation_id'] == curation_id)]
        except KeyError:
            self.log.warn("article_id and curation_id not in qualtrics survey !")
            response_df = pd.DataFrame()

        if not response_df.empty:
            self.log.info("Unique match based on article_id or curation_id !")
            if response_df.shape[0] != 1:
                self.log.warn("More than one entries found !!!")
            print(response_df[cols_order].to_markdown())
        else:
            self.log.info("Unable to identify based on article_id or curation_id ...")
            self.log.info("Attempting to identify with name ...")

            response_df = qualtrics_df[(qualtrics_df['Q4_1'] == dn_dict['fullName']) |
                                       (qualtrics_df['Q4_1'] == dn_dict['simplify_fullName']) |
                                       (qualtrics_df['Q4_2'] == dn_dict['depositor_email'])]

            # Identify corresponding author cases if different from depositor name
            if not dn_dict['self_deposit'] and not response_df.empty:
                self.log.info("Not self-deposit. Identifying based on corresponding author as well ...")
                df_select = response_df[(response_df['Q6_1'] == dn_dict['authors'][0])]
                if df_select.empty:
                    self.log.warn("Unable to identify based on corresponding author")
                    self.log.info("Listing all deposit agreements based on Depositor")
                    self.log.info(response_df[cols_order].to_markdown())
                else:
                    response_df = df_select

        if response_df.empty:
            self.log.warn("Empty DataFrame")
            raise ValueError
        else:
            if response_df.shape[0] == 1:
                response_dict = df_to_dict_single(response_df)
                self.log.info("Only one entry found!")
                self.log.info("Survey completed on {} for {}".format(response_dict['Date Completed'],
                                                                     response_dict['Q7']))
                return response_dict['ResponseId']
            else:
                self.log.warn("Multiple entries found")
                print(response_df[cols_order].to_markdown())
                raise ValueError

    def retrieve_deposit_agreement(self, dn_dict=None, ResponseId=None, browser=True):
        """Opens web browser to navigate to a page with Deposit Agreement Form"""

        if isinstance(ResponseId, type(None)):
            try:
                ResponseId = self.find_deposit_agreement(dn_dict)
                self.log.info("Qualtrics ResponseID : {}".format(ResponseId))
            except ValueError:
                self.log.warn("Error with retrieving ResponseId")
                self.log.info("PROMPT: If you wish, you can manually enter ResponseId to retrieve.")
                ResponseId = input("PROMPT: An EMPTY RETURN will generate a custom Qualtrics link to provide ... ")
                self.log.info(f"RESPONSE: {ResponseId}")

                if ResponseId == '':
                    custom_url = self.generate_url(dn_dict)
                    self.log.info("CUSTOM URL BELOW : ")
                    self.log.info(custom_url)
                    ResponseId = None

        if not isinstance(ResponseId, type(None)):
            if browser:
                self.log.info("Bringing up a window to login to Qualtrics with SSO ....")
                webbrowser.open('https://qualtrics.arizona.edu', new=2)
                input("Press the RETURN/ENTER key when you're signed on via SSO ... ")
            else:
                self.log.info("CLI: Not opening a browser!")
            full_url = '{}?RID={}&SID={}'.format(qualtrics_download_url, ResponseId,
                                                 self.survey_id)
            if browser:
                webbrowser.open(full_url, new=2)
            else:
                self.log.info("Here's the URL : ")
                self.log.info(full_url)

    def generate_url(self, dn_dict):
        """
        Purpose:
          Generate URL with Q_PopulateResponse, and article and curation ID
          query strings based on Figshare metadata
        """

        populate_response_dict = dict()
        populate_response_dict['QID4'] = {"1": dn_dict['fullName'],
                                          "2": dn_dict['depositor_email']}
        populate_response_dict['QID7'] = dn_dict['title']

        json_txt = quote(json.dumps(populate_response_dict), safe=url_safe)

        query_str_dict = {'article_id': dn_dict['article_id'],
                          'curation_id': dn_dict['curation_id'],
                          'Q_PopulateResponse': json_txt}

        full_url = f'{qualtrics_generate_url}{self.survey_id}?' + \
                   urlencode(query_str_dict, safe=url_safe, quote_via=quote)

        return full_url
