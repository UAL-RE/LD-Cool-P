from os.path import join, exists
from os import makedirs, chmod

# Logging
from ldcoolp.logger import log_stdout

# Admin
from ldcoolp.admin import move

# Curation
from ldcoolp.curation.retrieve import download_files
from ldcoolp.curation.reports import review_report
from ldcoolp.curation.depositor_name import DepositorName
from ldcoolp.curation.inspection.readme import ReadmeClass

# API
from figshare.figshare import Figshare
from ldcoolp.curation.api.figshare import FigshareInstituteAdmin
from ldcoolp.curation.api.qualtrics import Qualtrics

# Read in default configuration settings
from ..config import root_directory_main
from ..config import todo_folder, folder_copy_data, folder_data
from ..config import stage_flag
from ..config import api_token
from ..config import qualtrics_survey_id, qualtrics_token, qualtrics_dataCenter

'''
if api_token is None or api_token == "***override***":
    print("ERROR: figshare api_token not available from config file")
    api_token = input("Provide figshare token through prompt : ")

fs = Figshare(token=api_token, private=True, stage=stage_flag)
fs_admin = FigshareInstituteAdmin(token=api_token, stage=stage_flag)

acct_df = fs_admin.get_account_list()
'''

if qualtrics_survey_id is None or qualtrics_survey_id == "***override***":
    qualtrics_survey_id = input("Provide Qualtrics Survey ID through prompt : ")

if qualtrics_token is None or qualtrics_token == "***override***":
    qualtrics_token = input("Provide Qualtrics API token through prompt : ")

if qualtrics_dataCenter is None or qualtrics_dataCenter == "***override***":
    qualtrics_dataCenter = input("Provide Qualtrics dataCenter through prompt : ")

root_directory = join(root_directory_main, todo_folder)


class PrerequisiteWorkflow:
    """
    Purpose:
      Workflow class that follows our initial set-up to:
       1. Retrieve the data for a given deposit
       2. Set permissions and ownership (the latter needs to be tested and performed)
       3. Download curatorial review report
       4. Download Qualtrics Deposit Agreement form
       5. Check the README file

    """
    def __init__(self, article_id, fs_admin, fs, log=None, url_open=False):
        self.root_directory = root_directory
        self.article_id = article_id
        self.fs_admin = fs_admin
        self.fs = fs

        # If log is not defined, then output log to stdout
        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
            self.log = log

        self.dn = DepositorName(self.article_id, self.fs_admin, log=self.log)
        self.data_directory = join(self.dn.folderName, folder_data)

        self.copy_data_directory = join(self.dn.folderName, folder_copy_data)
        self.url_open = url_open

        # Check if dataset has been retrieved
        try:
            source_stage = move.get_source_stage(self.dn.folderName,
                                                 log=self.log, verbose=False)
            self.log.warn(f"Curation folder exists in {source_stage}. Will not retrieve!")
            self.new_set = False
        except FileNotFoundError:
            self.new_set = True
            # Create folders
            self.make_folders()

    def reserve_doi(self):
        # Mint DOI if this has not been done
        doi_string = self.fs_admin.reserve_doi(self.article_id)

        return doi_string

    def make_folders(self):
        # Create and set permissions to rwx
        full_data_path = join(self.root_directory, self.data_directory)
        if not exists(full_data_path):
            self.log.info(f"Creating folder : {full_data_path}")
            makedirs(full_data_path)
            chmod(full_data_path, 0o777)

        full_copy_data_path = join(self.root_directory, self.copy_data_directory)
        if not exists(full_copy_data_path):
            self.log.info(f"Creating folder : {full_copy_data_path}")
            makedirs(full_copy_data_path)
            chmod(full_copy_data_path, 0o777)

    def download_data(self):
        if self.new_set:
            download_files(self.article_id, fs=self.fs,
                           root_directory=self.root_directory,
                           data_directory=self.data_directory,
                           log=self.log, url_open=self.url_open)

    def download_report(self):
        if self.new_set:
            review_report(self.dn.folderName, log=self.log)

    def move_to_next(self):
        move.move_to_next(self.dn.folderName, log=self.log)


def workflow(article_id, url_open=False, browser=True, log=None):
    """
    Purpose:
      This function follows our initial set-up to:
       1. Retrieve the data for a given deposit
       2. Set permissions and ownership (the latter needs to be tested and performed)
       3. Download curatorial review report
       4. Download Qualtrics Deposit Agreement form
       5. Check the README file

    :param article_id: str or int, Figshare article id
    :param url_open: bool indicates using urlopen over urlretrieve. Default: False
    :param browser: bool indicates opening a web browser for Qualtrics survey. Default: True
    :param log: logger.LogClass object. Default is stdout via python logging
    """

    # If log is not defined, then output log to stdout
    if isinstance(log, type(None)):
        log = log_stdout()

    # Define Figshare API objects
    fs = Figshare(token=api_token, private=True, stage=stage_flag)
    fs_admin = FigshareInstituteAdmin(token=api_token, stage=stage_flag,
                                      log=log)

    pw = PrerequisiteWorkflow(article_id, fs_admin, fs, log=log,
                              url_open=url_open)

    # Perform prerequisite workflow if dataset is entirely new
    if pw.new_set:
        # Check if a DOI is reserved. If not, reserve DOI
        pw.reserve_doi()

        # Retrieve data and place in 1.ToDo curation folder
        pw.download_data()

        # Download curation report
        pw.download_report()

        # Download Qualtrics deposit agreement form
        q = Qualtrics(qualtrics_dataCenter, qualtrics_token,
                      qualtrics_survey_id, log=log)
        q.retrieve_deposit_agreement(pw.dn.name_dict, browser=browser)

        # Check for README file and create one if it does not exist
        rc = ReadmeClass(pw.dn, log=log)
        rc.main()

        # Move to next curation stage, 2.UnderReview curation folder
        if rc.template_source != 'unknown':
            log.info("PROMPT: Do you wish to move deposit to the next curation stage?")
            user_response = input("PROMPT: Type 'Yes'/'yes'. Anything else will skip : ")
            log.info(f"RESPONSE: {user_response}")
            if user_response.lower() == 'yes':
                pw.move_to_next()
