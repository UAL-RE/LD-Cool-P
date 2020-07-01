import configparser
from os.path import join, exists
from os import makedirs, chmod

# Admin
from ..admin import move

# Curation
from ldcoolp.curation.retrieve import download_files
from ldcoolp.curation.reports import review_report
from ldcoolp.curation.depositor_name import DepositorName
from ldcoolp.curation.inspection.readme import ReadmeClass

# API
from figshare.figshare import Figshare
from ldcoolp.curation.api.figshare import FigshareInstituteAdmin
from ldcoolp.curation.api.qualtrics import Qualtrics

# Read in default configuration file
from ldcoolp import config_file
config = configparser.ConfigParser()
config.read(config_file)

source = config.get('curation', 'source')
root_directory0 = config.get('curation', '{}_path'.format(source))

folder_todo = config.get('curation', 'folder_todo')
folder_data = config.get('curation', 'folder_data')
folder_copy_data = config.get('curation', 'folder_copy_data')

root_directory = join(root_directory0, folder_todo)

api_token = config.get('global', 'api_token')
if api_token is None or api_token == "***override***":
    print("ERROR: figshare api_token not available from config file")
    api_token = input("Provide figshare token through prompt : ")

fs = Figshare(token=api_token, private=True)
fs_admin = FigshareInstituteAdmin(token=api_token)

acct_df = fs_admin.get_account_list()

qualtrics_survey_id = config.get('curation', 'qualtrics_survey_id')
if qualtrics_survey_id is None or qualtrics_survey_id == "***override***":
    qualtrics_survey_id = input("Provide Qualtrics Survey ID through prompt : ")

qualtrics_token = config.get('curation', 'qualtrics_token')
if qualtrics_token is None or qualtrics_token == "***override***":
    qualtrics_token = input("Provide Qualtrics API token through prompt : ")

qualtrics_dataCenter = config.get('curation', 'qualtrics_dataCenter')
if qualtrics_dataCenter is None or qualtrics_dataCenter == "***override***":
    qualtrics_dataCenter = input("Provide Qualtrics dataCenter through prompt : ")


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
    def __init__(self, article_id):
        self.root_directory = root_directory
        self.article_id = article_id
        self.dn = DepositorName(self.article_id, fs_admin)
        self.data_directory = join(self.dn.folderName, folder_data)
        self.copy_data_directory = join(self.dn.folderName, folder_copy_data)

        self.make_folders()

    def make_folders(self):
        # Create and set permissions to rwx
        full_data_path = join(self.root_directory, self.data_directory)
        if not exists(full_data_path):
            makedirs(full_data_path)
            chmod(full_data_path, 0o777)

        full_copy_data_path = join(self.root_directory, self.copy_data_directory)
        if not exists(full_copy_data_path):
            makedirs(full_copy_data_path)
            chmod(full_copy_data_path, 0o777)

    def download_data(self):
        download_files(self.article_id, fs=fs,
                       root_directory=self.root_directory,
                       data_directory=self.data_directory)

    def download_report(self):
        review_report(self.dn.folderName)

    def move_to_next(self):
        move.move_to_next(self.dn.folderName)


def workflow(article_id):
    """
    Purpose:
      This function follows our initial set-up to:
       1. Retrieve the data for a given deposit
       2. Set permissions and ownership (the latter needs to be tested and performed)
       3. Download curatorial review report
       4. Download Qualtrics Deposit Agreement form
       5. Check the README file

    :param article_id:
    :return:
    """

    pw = PrerequisiteWorkflow(article_id)

    # Retrieve data and place in 1.ToDo curation folder
    pw.download_data()

    # Download curation report
    pw.download_report()

    # Download Qualtrics deposit agreement form
    q = Qualtrics(qualtrics_dataCenter, qualtrics_token, qualtrics_survey_id)
    q.retrieve_deposit_agreement(pw.dn.name_dict)

    # Move to next curation stage, 2.UnderReview curation folder
    pw.move_to_next()

    # Check for README file and create one if it does not exist
    rc = ReadmeClass(pw.dn)
    rc.check_exists()
