from os.path import join, exists
from os import makedirs, chmod

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
from ..config import config_default_dict


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
    def __init__(self, article_id, url_open=False, config_dict=config_default_dict):
        self.mc = move.MoveClass(curation_dict=config_dict['curation'])

        self.root_directory = join(self.mc.root_directory_main, self.mc.todo_folder)

        self.article_id = article_id

        self.curation_dict = config_dict['curation']
        self.figshare_dict = config_dict['figshare']

        self.fs = Figshare(token=self.figshare_dict['api_token'], private=True,
                           stage=self.figshare_dict['stage'])
        self.fs_admin = FigshareInstituteAdmin(figshare_dict=self.figshare_dict)

        self.dn = DepositorName(self.article_id, self.fs_admin)
        self.data_directory = join(self.dn.folderName,
                                   self.curation_dict['folder_data'])

        self.copy_data_directory = join(self.dn.folderName,
                                        self.curation_dict['folder_copy_data'])
        self.url_open = url_open

        # Check if dataset has been retrieved
        try:
            source_stage = self.mc.get_source_stage(self.dn.folderName)
            print(f"WARNING: Curation folder exists in {source_stage}. Will not retrieve!")
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
            makedirs(full_data_path)
            chmod(full_data_path, 0o777)

        full_copy_data_path = join(self.root_directory, self.copy_data_directory)
        if not exists(full_copy_data_path):
            makedirs(full_copy_data_path)
            chmod(full_copy_data_path, 0o777)

    def download_data(self):
        if self.new_set:
            download_files(self.article_id, self.fs,
                           root_directory=self.root_directory,
                           data_directory=self.data_directory,
                           url_open=self.url_open)

    def download_report(self):
        if self.new_set:
            review_report(self.dn.folderName, curation_dict=self.curation_dict)

    def move_to_next(self):
        self.mc.move_to_next(self.dn.folderName)


def workflow(article_id, url_open=False, browser=True, config_dict=config_default_dict):
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
    :param browser: bool to open a web browser of Qualtrics form. Default: True
    :param config_dict: dict of dict with hierarchy of sections
           (figshare, curation, qualtrics) follow by options
    """

    pw = PrerequisiteWorkflow(article_id, url_open=url_open, config_dict=config_dict)

    # Perform prerequisite workflow if dataset is entirely new
    if pw.new_set:
        # Check if a DOI is reserved. If not, reserve DOI
        pw.reserve_doi()

        # Retrieve data and place in 1.ToDo curation folder
        pw.download_data()

        # Download curation report
        pw.download_report()

        # Download Qualtrics deposit agreement form
        q = Qualtrics(qualtrics_dict=config_dict['qualtrics'])
        q.retrieve_deposit_agreement(pw.dn.name_dict, browser=browser)

        # Check for README file and create one if it does not exist
        rc = ReadmeClass(pw.dn, curation_dict=config_dict['curation'])
        rc.main()

        # Move to next curation stage, 2.UnderReview curation folder
        if rc.template_source != 'unknown':
            print("Do you wish to move deposit to the next curation stage?")
            user_response = input("Type 'Yes'/'yes'. Anything else will skip : ")
            if user_response.lower == 'yes':
                pw.move_to_next()
