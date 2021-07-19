from os.path import join, exists
from os import makedirs, chmod

# Logging
from redata.commons.logger import log_stdout

# Admin
from ldcoolp.admin import move

# Curation
from ldcoolp.curation.retrieve import download_files
from ldcoolp.curation.reports import review_report
from ldcoolp.curation.depositor_name import DepositorName
from ldcoolp.curation.inspection.readme import ReadmeClass

# Metadata
from .metadata import save_metadata

# API
from figshare.figshare import Figshare
from ldcoolp_figshare import FigshareInstituteAdmin
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

    def __init__(self, article_id, log=None,
                 config_dict=config_default_dict,
                 metadata_only=False):

        # If log is not defined, then output log to stdout
        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
            self.log = log

        self.mc = move.MoveClass(curation_dict=config_dict['curation'], log=self.log)

        self.root_directory = join(self.mc.root_directory_main, self.mc.todo_folder)

        self.article_id = article_id

        self.curation_dict = config_dict['curation']
        self.figshare_dict = config_dict['figshare']

        self.fs = Figshare(token=self.figshare_dict['token'], private=True,
                           stage=self.figshare_dict['stage'])
        self.fs_admin = FigshareInstituteAdmin(**self.figshare_dict, log=self.log)

        self.dn = DepositorName(self.article_id, self.fs_admin, log=self.log)

        # Sub-folders for data curation workflow
        self.data_directory = join(self.dn.folderName,
                                   self.curation_dict['folder_data'])
        self.copy_data_directory = join(self.dn.folderName,
                                        self.curation_dict['folder_copy_data'])
        self.metadata_directory = join(self.dn.folderName,
                                       self.curation_dict['folder_metadata'])

        self.metadata_only = metadata_only

        # Check if deposit is not deleted by user
        if self.dn.curation_dict['status'] == 'closed':
            self.log.warning(
                "This deposit was archived for one of many reasons!")
            self.log.info(f"resolution_comment metadata info: "
                          f"'{self.dn.curation_dict['resolution_comment']}'")
            self.log.warning("Stopping data curation for this deposit")
            raise SystemError

        # Check if dataset has been retrieved
        try:
            source_stage = self.mc.get_source_stage(self.dn.folderName, verbose=False)
            self.log.warn(f"Curation folder exists in {source_stage}. Will not retrieve!")
            self.new_set = False
        except FileNotFoundError:
            self.new_set = True
            # Create folders
            self.make_folders()
            self.write_curation_metadata()

    def reserve_doi(self):
        # Mint DOI if this has not been done
        doi_string = self.fs_admin.reserve_doi(self.article_id)

        return doi_string

    def make_folders(self):
        # Create and set permissions to rwx
        self.log.info("")
        self.log.info("** CREATING ORGANIZATIONAL STRUCTURE **")

        sub_dirs = [self.data_directory,
                    self.copy_data_directory,
                    self.metadata_directory]
        for sub_dir in sub_dirs:
            full_data_path = join(self.root_directory, sub_dir)
            if not exists(full_data_path):
                self.log.info(f"Creating folder : {full_data_path}")
                makedirs(full_data_path)
                chmod(full_data_path, 0o777)

    def write_curation_metadata(self):
        """Write metadata from Figshare curation response"""
        out_file_prefix = f"curation_original_{self.article_id}"
        save_metadata(self.dn.curation_dict, out_file_prefix,
                      root_directory=self.root_directory,
                      metadata_directory=self.metadata_directory,
                      save_csv=False, log=self.log)

    def download_data(self):
        if self.new_set:
            download_files(self.article_id, self.fs,
                           root_directory=self.root_directory,
                           data_directory=self.data_directory,
                           metadata_directory=self.metadata_directory,
                           metadata_only=self.metadata_only, log=self.log)

    def download_report(self):
        if self.new_set:
            review_report(self.dn.folderName, curation_dict=self.curation_dict,
                          log=self.log)

    def move_to_next(self):
        self.mc.move_to_next(self.dn.folderName)


def workflow(article_id, browser=True, log=None,
             config_dict=config_default_dict, metadata_only=False):
    """
    Purpose:
      This function follows our initial set-up to:
       1. Retrieve the data for a given deposit
       2. Set permissions and ownership (the latter needs to be tested and performed)
       3. Download curatorial review report
       4. Download Qualtrics Deposit Agreement form
       5. Check the README file

    :param article_id: str or int, Figshare article id
    :param browser: bool indicates opening a web browser for Qualtrics survey. Default: True
    :param log: logger.LogClass object. Default is stdout via python logging
    :param config_dict: dict of dict with hierarchy of sections
           (figshare, curation, qualtrics) follow by options
    :param metadata_only: When True, only downloads the item metadata.
    """

    # If log is not defined, then output log to stdout
    if isinstance(log, type(None)):
        log = log_stdout()

    try:
        pw = PrerequisiteWorkflow(article_id, log=log,
                                  config_dict=config_dict,
                                  metadata_only=metadata_only)
    except SystemError:
        return

    # Perform prerequisite workflow if dataset is entirely new
    if pw.new_set:
        # Check if a DOI is reserved. If not, reserve DOI
        pw.reserve_doi()

        # Retrieve data and place in 1.ToDo curation folder
        pw.download_data()

        # Download curation report
        pw.download_report()

        # Download Qualtrics deposit agreement form
        curation_dict = config_dict['curation']
        out_path = join(
            curation_dict[curation_dict['parent_dir']],
            curation_dict['folder_todo'],
            pw.dn.folderName,
            curation_dict['folder_ual_rdm'],
        )
        log.debug(f"out_path: {out_path}")
        q = Qualtrics(config_dict=config_dict, log=log)
        q.retrieve_deposit_agreement(pw.dn, out_path=out_path,
                                     browser=browser)

        # Check for README file and create one if it does not exist
        rc = ReadmeClass(pw.dn, log=log, config_dict=config_dict, q=q)
        try:
            rc.main()

            # Move to next curation stage, 2.UnderReview curation folder
            if rc.template_source != 'unknown':
                log.info("PROMPT: Do you wish to move deposit to the next curation stage?")
                user_response = input("PROMPT: Type 'Yes'/'yes'. Anything else will skip : ")
                log.info(f"RESPONSE: {user_response}")
                if user_response.lower() == 'yes':
                    pw.move_to_next()
                else:
                    log.info("Skipping move ...")
        except SystemExit as msg:
            log.warning(msg)
            log.info(" > To construct, run the `update_readme` command")

