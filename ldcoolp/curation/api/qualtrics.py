import time
from typing import Any, Tuple

# NOTE: Refactor to use pathlib.Path instead of os.path for modern path handling
from os.path import join
import io
from os import remove
from functools import reduce

# base64 encoding/decoding
import base64

# Text handling for README - not using starting in v0.17.1
# from html2text import html2text

# CSV handling
import zipfile
import pandas as pd

# URL handling
import requests
import json
from urllib.parse import quote, urlencode
from urllib.request import urlretrieve
from urllib.error import HTTPError
import webbrowser

# Convert single-entry DataFrame to dictionary
from ldcoolp.curation import df_to_dict_single
from ldcoolp.curation import metadata
from ldcoolp.admin import move

# Logging
from redata.commons.logger import log_stdout
import logging

# API
from figshare.figshare import issue_request

# Read in default configuration settings
from ..depositor_name import DepositorName
from ...config import config_default_dict
from ..pdf_generator import DepositAgreementBuilder

# for quote and urlencode
url_safe = '/ {},:"?=@%&'

# Column order for markdown print-out of Qualtrics table
cols_order = ['ResponseId', 'SurveyID', 'Q4_1', 'Q5', 'Q6_1', 'Q7']

readme_cols_order = ['ResponseId', 'SurveyID', 'article_id', 'curation_id']

readme_custom_content = ['cite', 'summary', 'files', 'materials', 'contrib', 'notes']


class Qualtrics:
    """
    Purpose:
      A Python interface for interaction with Qualtrics API for Deposit
      Agreement form survey

    :param config_dict: Dict that contains LD-Cool-P configuration.

      Default: config_default_dict from config/default.ini

    Attributes
    ----------
    dict : dict
      Qualtrics configuration dictionary

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

    get_survey_responses(survey_id)
      Retrieve pandas DataFrame containing responses for a survey
      See: https://api.qualtrics.com/docs/getting-survey-responses-via-the-new-export-apis

    find_deposit_agreement(dn)
      Call get_survey_responses() and identify response that matches based on
      depositor name (implemented) and deposit title (to be implemented).
      Returns ResponseID if a unique match is available

    retrieve_deposit_agreement(dn=, ResponseId=, browser=True)
      Opens up web browser to an HTML page containing the deposit agreement.
      It will call find_deposit_agreement() with DepositorName dict if
      ResponseId is not provided. Otherwise, it will use the provided
      ResponseId. Note that either dn or ResponseId must be provided

    generate_url(dn_dict)
      Generate URL with customized query strings based on Figshare metadata
    """

    def __init__(self, config_dict=config_default_dict,
                 mc: move.MoveClass = None,
                 log=None, interactive=True):

        self.interactive = interactive

        self.curation_dict = config_dict['curation']
        self.dict = config_dict['qualtrics']
        self.token = self.dict['token']
        self.data_center = self.dict['datacenter']

        self.baseurl = f"https://{self.data_center}.qualtrics.com/API/v3/"
        self.headers = {
            "X-API-TOKEN": self.token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self.survey_id = self.dict['survey_id']
        self.file_format = 'csv'

        self.readme_survey_id = self.dict['readme_survey_id']

        # Initialize Deposit Agreement info
        self.da_response_id: str = ''
        self.da_survey_id: str = ''

        # Logging
        self.file_logging = False
        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
            self.log = log
            for handler in log.handlers:
                if isinstance(handler, logging.FileHandler):
                    self.log_filename = handler.baseFilename
                    self.file_logging = True

        if mc:
            self.mc = mc
        else:
            self.mc = move.MoveClass(curation_dict=self.curation_dict)

    def endpoint(self, link):
        """Concatenate the endpoint to the baseurl"""

        return join(self.baseurl, link)

    def list_surveys(self):
        """Return dictionary containing all surveys for a user"""

        url = self.endpoint('surveys')
        survey_dict = issue_request('GET', url, headers=self.headers)

        return survey_dict

    def get_survey_responses(self, survey_id, verbose=False):
        """Retrieve pandas DataFrame containing responses for a survey"""

        progress_status = "inProgress"

        download_url = self.endpoint(f"surveys/{survey_id}/export-responses")

        # Create Data Export
        download_payload = {"format": self.file_format}
        download_response = issue_request("POST", download_url, data=download_payload,
                                          headers=self.headers)
        progress_id = download_response["result"]["progressId"]

        # Check on Data Export Progress and waiting until export is ready
        while progress_status != "complete" and progress_status != "failed":
            if verbose:
                self.log.debug(f"progress_status: {progress_status}")
            check_url = join(download_url, progress_id)
            check_response = issue_request("GET", check_url, headers=self.headers)
            check_progress = check_response["result"]["percentComplete"]
            if verbose:
                self.log.debug(f"Download is {str(check_progress)}% complete")
            progress_status = check_response["result"]["status"]

        # Check for error
        if progress_status == "failed":
            err = "export failed"
            self.log.warn(err)
            raise Exception(err)

        file_id = check_response["result"]["fileId"]

        # Retrieve zipfile and extract and read in CSV into pandas DataFrame
        download_url = join(download_url, f'{file_id}/file')
        requestDownload = requests.request("GET", download_url, headers=self.headers, stream=True)
        input_zip = zipfile.ZipFile(io.BytesIO(requestDownload.content))
        csv_filename = input_zip.namelist()[0]
        input_zip.extract(csv_filename)

        response_df = pd.read_csv(csv_filename)
        remove(csv_filename)

        return response_df

    def merge_survey(self) -> pd.DataFrame:
        """
        Constructed a merge pandas dataframe of all Qualtrics survey

        :return: Merged pandas DataFrame
        """

        df_list = []
        for survey_id in self.survey_id:
            self.log.debug(f"Reading: {survey_id}")
            temp_df = self.get_survey_responses(survey_id)
            df_list.append(temp_df[2:])

        df_col = reduce(pd.Index.union, (df.columns for df in df_list))

        merged_df = pd.DataFrame()
        for df in df_list:
            temp_df = df.reindex(columns=df_col, fill_value=0)
            merged_df = pd.concat([merged_df, temp_df], ignore_index=True)
        return merged_df

    def get_survey_response(self, survey_id: str, ResponseId: str) -> pd.DataFrame:
        """
        Return pandas DataFrame for a given ResponseId from survey_id
        """
        qualtrics_df = self.get_survey_responses(survey_id)
        response_df = qualtrics_df[(qualtrics_df['ResponseId'] == ResponseId)]
        if not response_df.empty:
            self.log.info(f"Match found with {ResponseId}")
        return response_df

    def pandas_write_buffer(self, df):
        """Write pandas content via to_markdown() to logfile"""

        buffer = io.StringIO()
        df.to_markdown(buffer)
        print(buffer.getvalue())
        if self.file_logging:
            with open(self.log_filename, mode='a') as f:
                print(buffer.getvalue(), file=f)
        buffer.close()

    def lookup_survey_shortname(self, lookup_survey_id):
        """Return survey shortname"""
        dict0 = dict(zip(self.survey_id, self.dict['survey_shortname']))
        try:
            return dict0[lookup_survey_id]
        except KeyError:
            self.log.warn("survey_id not found among list")

    def find_deposit_agreement(self, dn: DepositorName):
        """Get Response ID based on a match search for depositor name"""

        merged_df = self.merge_survey()

        dn_dict = dn.name_dict

        # First perform search via article_id or curation_id
        self.log.info("Attempting to identify using article_id or curation_id ...")
        article_id = str(dn_dict['article_id'])
        curation_id = str(dn_dict['curation_id'])

        try:
            response_df = merged_df[(merged_df['article_id'] == article_id) |
                                    (merged_df['curation_id'] == curation_id)]
        except KeyError:
            self.log.warn("article_id and curation_id not in qualtrics survey !")
            response_df = pd.DataFrame()

        if not response_df.empty:
            self.log.info("Unique match based on article_id or curation_id !")
            if response_df.shape[0] != 1:
                self.log.warn("More than one entries found !!!")
        else:
            self.log.info("Unable to identify based on article_id or curation_id ...")
            self.log.info("Attempting to identify with name ...")

            response_df = merged_df[(merged_df['Q4_1'] == dn_dict['fullName']) |
                                    (merged_df['Q4_1'] == dn_dict['simplify_fullName']) |
                                    (merged_df['Q4_2'] == dn_dict['depositor_email'])]

            # Identify corresponding author cases if different from depositor name
            if not dn_dict['self_deposit'] and not response_df.empty:
                self.log.info("Not self-deposit. Identifying based on corresponding author as well ...")
                df_select = response_df[(response_df['Q6_1'] == dn_dict['authors'][0])]
                if df_select.empty:
                    self.log.warn("Unable to identify based on corresponding author")
                    self.log.info("Listing all deposit agreements based on Depositor")

                    self.pandas_write_buffer(response_df[cols_order])
                else:
                    response_df = df_select

        if response_df.empty:
            self.log.warn("Empty DataFrame")
            raise ValueError
        else:
            if response_df.shape[0] == 1:
                response_dict = df_to_dict_single(response_df)
                self.save_metadata(response_dict, dn, out_file_prefix=
                                   f'deposit_agreement_original_{article_id}')
                self.pandas_write_buffer(response_df[cols_order])
                self.log.info("Only one entry found!")
                self.log.info(f"Survey completed on {response_dict['Date Completed']}")
                self.log.info(f" ... for {response_dict['Q7']}")
                survey_shortname = \
                    self.lookup_survey_shortname(response_dict['SurveyID'])
                self.log.info(f"Survey name: {survey_shortname}")
                self.da_response_id = response_dict['ResponseId']
                self.da_survey_id = response_dict['SurveyID']
                return response_dict['ResponseId'], response_dict['SurveyID']
            else:
                self.log.warn("Multiple entries found")

                self.pandas_write_buffer(response_df[cols_order])

                raise ValueError

    def retrieve_deposit_agreement(self, dn=None, ResponseId=None, out_path='',
                                   browser=True):
        """Opens web browser to navigate to a page with Deposit Agreement Form"""

        self.log.info("")
        self.log.info("** RETRIEVING DEPOSIT AGREEMENT **")

        if isinstance(ResponseId, type(None)):
            try:
                ResponseId, SurveyId = self.find_deposit_agreement(dn)
                self.log.info(f"Qualtrics ResponseID : {ResponseId}")
                self.log.info(f"Qualtrics SurveyID : {SurveyId}")
            except ValueError:
                self.log.warn("Error with retrieving ResponseId and SurveyId")
                self.log.info("PROMPT: If you wish, you can manually enter ResponseId to retrieve.")
                if self.interactive:
                    ResponseId = input("PROMPT: An EMPTY RETURN will generate a custom Qualtrics link to provide ... ")
                    self.log.info(f"RESPONSE: {ResponseId}")
                    self.log.info("PROMPT: If you wish, you can manually enter SurveyId to retrieve.")
                    SurveyId = input("PROMPT: An EMPTY RETURN will generate a custom Qualtrics link to provide ... ")
                    self.log.info(f"RESPONSE: {SurveyId}")
                else:
                    self.log.info("Interactive mode disabled. Skipping manual input")
                    ResponseId = ''
                    SurveyId = ''

                if ResponseId == '' or SurveyId == '':
                    custom_url = self.generate_url(dn.name_dict)
                    self.log.info("CUSTOM URL BELOW : ")
                    self.log.info(custom_url)
                    ResponseId = None

                if ResponseId != '':
                    self.da_response_id = ResponseId

                if SurveyId != '':
                    self.da_survey_id = SurveyId

        if not isinstance(ResponseId, type(None)):
            self.da_response_id = ResponseId

            if browser:
                self.log.info("Bringing up a window to login to Qualtrics with SSO ....")
                webbrowser.open('https://qualtrics.arizona.edu', new=2)
                input("Press the RETURN/ENTER key when you're signed on via SSO ... ")
            else:
                self.log.info("CLI: Not opening a browser!")

            full_url = f"{self.dict['download_url']}?RID={ResponseId}&SID={SurveyId}"

            # Retrieve PDF via direct URL link
            if out_path:
                if self.interactive:
                    pdf_url = 'retrieve'
                else:
                    pdf_url = ''
                while pdf_url == 'retrieve':
                    pdf_url = input("To retrieve PDF via API, provide PDF URL here. Hit enter to skip : ")

                    if not pdf_url:  # Skip PDF retrieval
                        break

                    if 'qualtrics.com' in pdf_url and pdf_url.endswith("format=pdf"):
                        self.log.info(f"RESPONSE: {pdf_url}")
                        try:
                            out_pdf = join(out_path, 'Deposit_Agreement.pdf')
                            urlretrieve(pdf_url, out_pdf)
                            break
                        except HTTPError:
                            self.log.warning("Unable to retrieve PDF")
                            pdf_url = 'retrieve'
                    else:
                        pdf_url = 'retrieve'
            else:
                self.log.warn("No out_path specified. Skipping PDF retrieval")

            if browser:
                webbrowser.open(full_url, new=2)
            else:
                self.log.info("Here's the URL : ")
                self.log.info(full_url)

    def _handle_api_response(self, response: requests.Response) -> dict[str, Any]:
        """
        Handle and validate a Qualtrics API response.

        Checks for HTTP errors, parses the JSON response payload, validates 
        the internal Qualtrics status (ensuring '200 - OK'), logs and raises any errors, 
        and returns the resulting data dictionary.

        :param response: The requests.Response object returned from an API call.
        :return: A dictionary containing the response result data.
        """

        response.raise_for_status()  # WARN: Raises exception
        res: dict[str, Any] = response.json()  # WARN: Raises exception

        if res["meta"]["httpStatus"] != "200 - OK":
            status = res["meta"]["httpStatus"]
            notice = res["meta"]["notice"]
            err_msg = f"Qualtrics Error: {status}: {notice}"
            raise Exception(err_msg)  # WARN: Raises exception

        return res.get("result", {})

    def get_raw_survey(self, survey_id: str) -> dict[str, Any]:
        """
        Retrieve the raw survey definition from the Qualtrics API.

        Sends a GET request to fetch the raw configuration and metadata
        for a specific survey, validates the HTTP status, and returns the result dictionary.

        :param survey_id: The Qualtrics survey ID (e.g., beginning with SV_*).
        :return: A dictionary containing the raw survey result data.
        """

        url = self.endpoint(f"surveys/{survey_id}")

        response = requests.get(url, headers=self.headers)

        return self._handle_api_response(response)

    def start_response_export(self, survey_id: str) -> tuple[str, str]:
        """
        Initiate an asynchronous response export for a Qualtrics survey.

        Sends a POST request to start exporting survey responses using
        preconfigured settings (such as CSV format and embedded data), and returns
        the progress tracking ID and initial export status.

        :param survey_id: The Qualtrics survey ID (e.g., beginning with SV_*).
        :return: A tuple containing (progress ID, initial status).
        """

        url = self.endpoint(f"surveys/{survey_id}/export-responses")
        payload = {
            "format": "csv",  # Allowed values: csv, json, ndjson, spss, tsv, xml
            "compress": True,  # Compress the final export file as a ZIP file unless the export is small.
            "limit": 25,  # Maximum number of responses to export.
            "useLabels": True,  # Not for json, ndjson format - Export the answer choice text instead of its numeric value.
            # NOTE: See https://api.qualtrics.com/6b00592b9c013-start-response-export#request-body
            # for additional options. Customize this payload as much as needed.
            "embeddedDataIds": [
                "article_id",
                "curation_id",
                "depositor_email",
            ],  
            "questionIds": [],
            "surveyMetadataIds": [
                "endDate",
                "status",
                "ipAddress",
                "finished",
                "recordedDate",
                "_recordId",
            ],
        }

        response = requests.post(url, headers=self.headers, json=payload)
        result: dict[str, Any] = self._handle_api_response(response)

        return result.get("progressId", ""), result.get("status", "")

    def check_export_progress_and_get_file_id(self, survey_id: str, progress_id: str) -> str:
        """
        Poll and monitor the progress of a Qualtrics response export.

        Repeatedly checks the export progress endpoint using the provided
        survey ID and progress ID until the export is complete or fails, then returns
        the resulting file ID for downloading.

        :param survey_id: The Qualtrics survey ID (e.g., beginning with SV_*).
        :param progress_id: The progress ID tracking the ongoing export task.
        :return: The unique file ID of the completed export.
        """

        url = self.endpoint(f"surveys/{survey_id}/export-responses/{progress_id}")

        self.log.info("Checking export progress")
        while True:
            response = requests.get(url, headers=self.headers)
            result: dict[str, Any] = self._handle_api_response(response)
            status = result.get("status", "")

            if status == "complete":
                if "fileId" not in result:
                    self.log.error("Qualtrics Export Completed but no `fileId` found.")
                    raise Exception("Qualtrics Export Completed but no `fileId` found.")

                file_id: str = result.get("fileId", "")
                self.log.info("Response exported")
                break
            elif status == "failed":
                error = result.get("error", {})
                err_msg = f"Qualtrics Export Failed: {error}"
                self.log.error(err_msg)
                raise Exception(err_msg)  # WARN: Raises exception

            time.sleep(3)
            self.log.info("...")

        return file_id

    def get_responses_from_file(self, survey_id: str, file_id: str) -> pd.DataFrame:
        """
        Download, extract, and load exported survey responses from a zip file.

        Requests the exported response archive using the survey ID and file ID,
        extracts the CSV file from the zip container, drops the Qualtrics metadata header rows,
        and returns the data as a pandas DataFrame.

        :param survey_id: The Qualtrics survey ID (e.g., beginning with SV_*).
        :param file_id: The unique file ID of the completed export.
        :return: A pandas DataFrame containing the survey responses.
        """

        url = self.endpoint(f"surveys/{survey_id}/export-responses/{file_id}/file")
        headers = {
            "X-API-TOKEN": self.token,
            "Accept": "application/octet-stream, application/json",
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # WARN: Raises exception

        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            if len(zf.namelist()) == 1:
                with zf.open(zf.namelist()[0]) as f:
                    response_df = pd.read_csv(f)
                    response_df.drop(index=[0, 1], inplace=True)
                    return response_df

            # NOTE: If multiple files are found, take note of the files and
            # process only the first file for now
            # WARN: Multiple files not tested, may require additional handling
            self.log.warning(f"Multiple files found in zip: {zf.namelist()}")
            for filename in zf.namelist():
                self.log.warning(f"    File: {filename}")

            self.log.warning("    Processing only the first file...")
            with zf.open(zf.namelist()[0]) as f:
                response_df = pd.read_csv(f)
                response_df.drop(index=[0, 1], inplace=True)
                return response_df

    def process_survey_questions(self, raw_survey: dict[str, Any]) -> dict[str, dict[str, str]]:
        """
        Process and structure raw survey questions from API data.

        Parses the raw survey definition to extract and standardize
        question attributes—such as sequence number, name, type, label, and text—while
        also extracting form sub-questions if the question type is a form selector.

        :param raw_survey: Dictionary containing raw survey metadata from Qualtrics.
        :return: A filtered dictionary of structured question details indexed by question ID.
        """

        if not raw_survey:
            return {}

        questions: dict[str, dict[str, Any]] = raw_survey.get("questions", {})
        filtered_questions: dict[str, dict[str, str]] = {}

        for qid, q_data in questions.items():
            q_type = q_data["questionType"]
            q_type_str = f"{q_type['type']}-{q_type['selector']}"

            base_dict = {
                "seq_no": int(q_data["questionName"].replace("Q", "")),
                "questionName": q_data["questionName"],
                "questionType": q_type_str,
                "questionLabel": q_data.get("questionLabel", ""),
                "questionText": q_data["questionText"],
            }

            if q_type["selector"] == "FORM" and "choices" in q_data:
                base_dict["formQuestions"] = [
                    choice["choiceText"] for choice in q_data["choices"].values()
                ]

            filtered_questions[qid] = base_dict

        return filtered_questions

    def get_matching_response_id(self, response_data: pd.DataFrame, filter_by: dict[str, Any]) -> str:
        """
        Filter survey response data and identify a matching response ID.

        This method filters the response DataFrame using specified key-value criteria,
        sorts the results by end date (most recent first), and returns the ResponseID
        for the matching entry. If multiple matches are found, it selects the top result.

        :param response_data: Pandas DataFrame containing survey responses.
        :param filter_by: Dictionary of column-value pairs used to filter responses.
        :return: The matching survey ResponseId as a string.
        """

        # Filter the response data
        for key, value in filter_by.items():
            if key not in response_data.columns:
                self.log.info(f"Column '{key}' not found in the response data.")
                continue
            response_data = response_data[response_data[key] == value].copy()

        response_data.sort_values(by=["EndDate"], ascending=[False], inplace=True)

        filtered_response_length = len(response_data)
        self.log.info(f"{filtered_response_length} response(s) found.")

        if filtered_response_length == 1:
            return str(response_data["ResponseId"].iloc[0])

        # if more that 1 response is found, ask for user input to select the response index
        # if user does not select a response, then return the latest response
        # if user selects a response, then return the selected response
        if filtered_response_length > 1:
            self.log.info("Multiple responses found:")
            for sl, records in enumerate(response_data.to_dict(orient="records")):
                self.log.info(f"    {sl: >2}:\n    {records}")

            # User input to select the response index
            selection = input(
                "\nEnter the index of the response to select "
                "(or press Enter to select the latest response):\n"
            )
            if not selection:
                self.log.info("No input provided. Selecting the latest response.")
                selection = "0"
            elif not selection.isdigit() or int(selection) < 0 or int(selection) >= filtered_response_length:
                self.log.warning("Invalid input. Selecting the latest response.")
                selection = "0"
            else:
                self.log.info(f"Selected response index: {selection}")

            return str(response_data["ResponseId"].iloc[int(selection)])

        # If no matching responses are found, log a warning and return an empty string
        self.log.warning("No matching responses found.")
        return ""

    def get_raw_survey_response(self, survey_id: str, response_id: str) -> dict[str, Any]:
        """
        Retrieve raw response details for a specific survey response from the Qualtrics API.

        Sends a GET request to fetch the raw response payload for a given
        response ID, validates the HTTP status, and returns the result dictionary.

        :param survey_id: The Qualtrics survey ID (e.g., beginning with SV_*).
        :param response_id: The specific survey response ID to retrieve.
        :return: A dictionary containing the raw response data result.
        """

        url = self.endpoint(f"surveys/{survey_id}/responses/{response_id}")

        response = requests.get(url, headers=self.headers)

        return self._handle_api_response(response)

    def process_survey_response(self, raw_response: dict[str, Any]) -> dict[str, Any]:
        """
        Process and clean raw survey response data.

        Extracts values and labels from the raw response, replaces
        values with human-readable label text where available, filters out
        internal display order keys (ending with '_DO'), and returns the
        cleaned response dictionary.

        :param raw_response: Raw survey response dictionary containing 'values' and 'labels'.
        :return: Cleaned response dictionary with human-readable text.
        """

        values: dict[str, Any] = raw_response.get("values", {})
        labels: dict[str, Any] = raw_response.get("labels", {})

        for k, v in labels.items():
            if k.endswith("_DO") and isinstance(v, list):
                del values[k]
            elif isinstance(v, str):
                values[k] = v
        return values

    def merge_question_response_data(
        self, questions: dict[str, Any], answers: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Merge survey questions with their corresponding response answers.

        Maps raw answer values to their respective question definitions 
        (handling standard questions and multi-part form inputs), appends any 
        unanswered or descriptive questions, sorts them by sequence number, and 
        separates non-question embedded metadata.

        :param questions: Dictionary of survey questions indexed by question ID.
        :param answers: Dictionary of raw survey response values and embedded data.
        :return: A tuple of (sorted merged Q&A dictionary, embedded data dictionary).
        """

        merged_qa: dict[str, Any] = {}
        embedded_data: dict[str, Any] = {}

        for key, value in answers.items():
            if not key.startswith("QID"):
                embedded_data[key] = value
                continue

            q_no, *ch_no = key.split("_")
            if q_no not in questions.keys():
                continue

            if ch_no and questions[q_no]["questionType"].endswith("FORM"):
                questions[q_no].setdefault("answer", []).append(value)
            else:
                questions[q_no]["answer"] = value

            merged_qa[q_no] = questions[q_no]

        # Add leftover descriptive questions or unanswered questions
        for qid, q_data in questions.items():
            if qid not in merged_qa:
                q_data["answer"] = ""
                merged_qa[qid] = q_data

        # sort qa_map by seq_no to maintain the order of questions as they appear in the survey
        merged_qa = dict(sorted(merged_qa.items(), key=lambda item: item[1]["seq_no"]))

        return merged_qa, embedded_data

    def generate_deposit_agreement_v2(self, dn, out_path: str) -> None:
        """
        Generate Deposit Agreement (Version 2.0) PDF and save its metadata.

        Fetches the survey questions and latest responses, matches
        the response to the depositor using their article ID, merges the
        question-answer pairs, builds the PDF deposit agreement, and saves
        the original metadata locally.

        :param dn: DepositorName object containing metadata (e.g., article_id).
        :param out_path: Directory path where the output PDF will be saved.
        :return: None
        """

        self.log.info("")
        self.log.info("** GENERATING DEPOSIT AGREEMENT (Version 2.0) **")
        self.log.info("This is a new Qualtrics survey for Deposit Agreement form")

        survey_id = self.dict["survey_id"][0]
        raw_survey = self.get_raw_survey(survey_id)

        survey_questions = self.process_survey_questions(raw_survey)

        progress_id, status = self.start_response_export(survey_id)
        self.log.info(f"Export Progress ID: {progress_id}, Status: {status}")

        file_id = self.check_export_progress_and_get_file_id(survey_id, progress_id)
        self.log.info(f"Export File ID: {file_id}")

        all_response = self.get_responses_from_file(survey_id, file_id)
        if all_response is None:
            self.log.error("No survey responses found.")
            return

        filter_by = {"article_id": dn.article_id}
        response_id = self.get_matching_response_id(all_response, filter_by)
        if not response_id:
            self.log.error("No matching survey response found.")
            return
        self.log.info(f"Matched Response ID: {response_id}")

        raw_response = self.get_raw_survey_response(survey_id, response_id)

        survey_response = self.process_survey_response(raw_response)

        merged_qa, embedded_data = self.merge_question_response_data(
            survey_questions, survey_response
        )

        if not (merged_qa or embedded_data):
            err_msg = "Either question-answer pairs or embedded data is missing for the given survey response."
            self.log.error(err_msg)
            raise ValueError(err_msg)  # WARN: Raises exception

        out_pdf = join(out_path, 'Deposit_Agreement.pdf')
        data = {"merged_qa": merged_qa, "embedded_data": embedded_data}

        builder = DepositAgreementBuilder()
        builder.generate(data, out_pdf)
        self.log.info(f"PDF generated successfully at: {out_pdf}")

        self.save_metadata(
            data, dn, out_file_prefix=f"deposit_agreement_original_{dn.article_id}"
        )

    def survey_specific(self, dn_dict: dict) -> Tuple[str, dict]:
        """
        Handles survey specifics for Qualtrics Deposit Agreement form
        Used by generate_url method

        :param dn_dict: DepositorName dictionary
        :return: survey_id and dict for Qualtrics links
        """

        populate_response_dict = dict()  # init

        def _std_populate_response_dict():
            populate_response_dict['QID4'] = {
                "1": dn_dict['fullName'],
                "2": dn_dict['depositor_email']
            }

        survey_id_idx = 0
        if 'survey_email' not in self.dict:
            self.log.debug("No survey_email settings")

            _std_populate_response_dict()
        else:
            if dn_dict['depositor_email'] in self.dict['survey_email']:
                survey_id_idx = self.dict['survey_email'].index(dn_dict['depositor_email'])

                authors = dn_dict['authors']
                populate_response_dict['QID4'] = {"1": authors[0]}
                # This populates Advisor info for Space Grant Deposits
                if self.dict['survey_shortname'][survey_id_idx] == "Space Grant":
                    populate_response_dict['QID11'] = {"1": authors[1]}
            else:
                _std_populate_response_dict()

        use_survey_id = self.survey_id[survey_id_idx]

        return use_survey_id, populate_response_dict

    def generate_da_url(self, dn_dict) -> str:
        """Generate URL for Deposit Agreement"""

        survey_id_idx = 0
        if dn_dict['depositor_email'] in self.dict['survey_email']:
            survey_id_idx = self.dict['survey_email'].index(dn_dict['depositor_email'])

        use_survey_id = self.survey_id[survey_id_idx]

        query_str_dict = {
            "article_id": dn_dict["article_id"],
            "curation_id": dn_dict["curation_id"],
            "dataset_title": dn_dict["title"],
            "depositor_name": dn_dict["simplify_fullName"],
            "depositor_email": dn_dict["depositor_email"],
        }

        full_url = f"{self.dict['generate_url']}{use_survey_id}?" + \
                   urlencode(query_str_dict, safe=url_safe, quote_via=quote)

        return full_url

    def generate_readme_url(self, dn):
        """Generate URL for README tool using Q_EED option"""

        df_curation = dn.curation_dict

        # Preferred citation
        single_str_citation = df_curation['item']['citation']

        # handle period in author list.  Assume no period in dataset title
        str_list = list([single_str_citation.split(').')[0] + '). '])
        str_list += [str_row + '.' for str_row in single_str_citation.split(').')[1].split('. ')]

        citation_list = [content for content in str_list[0:-2]]
        citation_list.append(f"{str_list[-2]} {str_list[-1]}")
        citation_list = ' <br> '.join(citation_list)

        # summary
        figshare_description = df_curation['item']['description']

        query_str_dict = {'article_id': dn.name_dict['article_id'],
                          'curation_id': dn.name_dict['curation_id'],
                          'title': dn.name_dict['title'],
                          'depositor_name': dn.name_dict['simplify_fullName'],
                          'preferred_citation': citation_list,
                          'license': df_curation['item']['license']['name'],
                          'summary': figshare_description}
        # doi
        if not df_curation['item']['doi']:  # empty case
            query_str_dict['doi'] = f"https://doi.org/10.25422/azu.data.{dn.name_dict['article_id']}"
        else:
            query_str_dict['doi'] = f"https://doi.org/{df_curation['item']['doi']}"

        # links
        if not df_curation['item']['references']:  # not empty case
            links = " <br> ".join(df_curation['item']['references'])
            query_str_dict['links'] = links

        # query_str_encode = str(query_str_dict).encode('base64', 'strict')
        q_eed = base64.urlsafe_b64encode(json.dumps(query_str_dict).encode()).decode()

        full_url = f"{self.dict['generate_url']}{self.readme_survey_id}?" + \
                   'Q_EED=' + q_eed

        return full_url

    def find_qualtrics_readme(self, dn: DepositorName):
        """Get Response ID based on a article_id,curation_id search"""

        dn_dict = dn.name_dict
        qualtrics_df = self.get_survey_responses(self.readme_survey_id)

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

        if response_df.empty:
            self.log.warn("Empty DataFrame")
            raise ValueError
        else:
            self.log.info("Unique match based on article_id or curation_id !")
            self.pandas_write_buffer(response_df[readme_cols_order])
            if response_df.shape[0] == 1:
                response_dict = df_to_dict_single(response_df)
                self.log.info("Only one entry found!")
                self.log.info(f"Survey completed on {response_dict['date_completed']}")
                self.log.info(f" ... for {response_dict['article_id']}")
                return response_dict['ResponseId'], response_df
            else:
                self.log.warn("Multiple entries found")
                raise ValueError

    def retrieve_qualtrics_readme(self, dn=None, ResponseId='', browser=True,
                                  save_metadata: bool = False):
        """Retrieve response to Qualtrics README form"""

        if ResponseId:
            response_df = self.get_survey_response(self.readme_survey_id, ResponseId)
        else:
            try:
                ResponseId, response_df = self.find_qualtrics_readme(dn)
                self.log.info(f"Qualtrics README ResponseID : {ResponseId}")
            except ValueError:
                self.log.warn("Error with retrieving ResponseId")
                self.log.info("PROMPT: If you wish, you can manually enter ResponseId to retrieve.")
                if self.interactive:
                    ResponseId = input("PROMPT: An EMPTY RETURN will generate a custom Qualtrics link to provide ... ")
                    self.log.info(f"RESPONSE: {ResponseId}")
                else:
                    self.log.info("Interactive mode disabled. Skipping manual input")
                    ResponseId = ''

                if ResponseId:
                    response_df = self.get_survey_response(self.readme_survey_id, ResponseId)
                else:
                    response_df = pd.DataFrame()
                    readme_url = self.generate_readme_url(dn)
                    self.log.info(f"README URL: {readme_url}")

        if response_df.empty:
            self.log.warn("Empty DataFrame")
            self.log.info("Filling with empty content")
            qualtrics_dict = {}
            for field in readme_custom_content:
                qualtrics_dict[field] = 'nan'
            qualtrics_dict['references'] = []
        else:
            qualtrics_dict = df_to_dict_single(response_df[readme_custom_content])
            for key in qualtrics_dict.keys():
                if isinstance(qualtrics_dict[key], float):
                    qualtrics_dict[key] = str(qualtrics_dict[key])

            # Separate cite, contrib for list style
            for field in ['cite', 'contrib']:
                if qualtrics_dict[field] != 'nan':
                    qualtrics_dict[field] = qualtrics_dict[field].split('\n')

            # Markdown files, materials
            for field in ['files', 'materials']:
                if qualtrics_dict[field] != 'nan':
                    if qualtrics_dict[field][0] == "'":
                        qualtrics_dict[field] = qualtrics_dict[field][1:]
                        self.log.debug(f"Removing extra single quote in {field} entry")

        # Retrieve corresponding author info and append
        self.log.info("Appending Deposit Agreement's Corresponding Author metadata")
        if not self.da_response_id:
            self.log.info("NO METADATA - Retrieving Deposit Agreement metadata")
            self.find_deposit_agreement(dn)
        else:
            self.log.info(f"Parsed ResponseId : {self.da_response_id}")
            self.log.info(f"Parsed SurveyID : {self.da_survey_id}")

        DA_response_df = self.get_survey_response(self.da_survey_id, self.da_response_id)
        DA_dict = df_to_dict_single(DA_response_df)
        qualtrics_dict['corr_author_fullname'] = DA_dict['Q6_1']
        qualtrics_dict['corr_author_email'] = DA_dict['Q6_2']
        qualtrics_dict['corr_author_affil'] = DA_dict['Q6_3']

        # Save Qualtrics README metadata
        if save_metadata:
            out_file_prefix = "qualtrics_readme_original_" + \
                              f"{dn.name_dict['article_id']}"
            self.save_metadata(qualtrics_dict, dn,
                               out_file_prefix=out_file_prefix)

        return qualtrics_dict

    def save_metadata(self, response_dict: dict, dn: DepositorName,
                      out_file_prefix: str = 'qualtrics'):
        """Save Qualtrics metadata to JSON file"""

        current_stage = self.mc.get_source_stage(dn.folderName)

        root_directory = join(
            self.curation_dict[self.curation_dict['parent_dir']],
            current_stage,
            dn.folderName
        )
        metadata_directory = self.curation_dict['folder_metadata']

        metadata.save_metadata(response_dict, out_file_prefix,
                               metadata_source='QUALTRICS',
                               root_directory=root_directory,
                               metadata_directory=metadata_directory,
                               log=self.log)
