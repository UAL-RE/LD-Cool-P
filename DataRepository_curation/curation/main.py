import configparser
from os.path import join

# Admin
from ..admin import move, permissions

# Curation
from DataRepository_curation.curation.retrieve import download_files
from DataRepository_curation.curation.reports import review_report
from DataRepository_curation.curation.depositor_name import DepositorName

# API
from figshare.figshare import Figshare
from DataRepository_curation.curation.api.figshare import FigshareInstituteAdmin
from DataRepository_curation.curation.api.qualtrics import Qualtrics

# Read in default configuration file
from DataRepository_curation import config_file
config = configparser.ConfigParser()
config.read(config_file)

source = config.get('curation', 'source')
root_directory0 = config.get('curation', '{}_path'.format(source))

folder_todo = config.get('curation', 'folder_todo')
folder_data = config.get('curation', 'folder_data')

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

    # Placeholder to download Qualtrics deposit agreement form
    q = Qualtrics(qualtrics_dataCenter, qualtrics_token, qualtrics_survey_id)
    try:
        ResponseID = q.find_deposit_agreement(pw.dn.name_dict)
        print("Qualtrics ResponseID : {}".format(ResponseID))
    except ValueError:
        print("Unable to obtain a unique match")

    # Move to next curation stage
    pw.move_to_next()

    # Placeholder to check for README file and create one if it doesn't exists
