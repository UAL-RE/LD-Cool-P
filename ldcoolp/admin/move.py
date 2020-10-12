from os.path import join, dirname, exists
from os import makedirs, chmod
import shutil
from glob import glob

# Logging
from ..logger import log_stdout

# Read in default configuration settings
from ..config import config_default_dict


class MoveClass:
    """
    Purpose:
      Python interface for administrative content move following curation workflow

    :param curation_dict: Dict that contains curation configuration.
      This should include:
       - parent_dir (str)
       - folder_todo (str)
       - folder_underreview (str)
       - folder_reviewed (str)
       - folder_published (str)
       - folder_rejected (str)

    :param log: logger.LogClass object. Default is stdout via python logging
    """

    def __init__(self, curation_dict=config_default_dict['curation'], log=None):

        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
            self.log = log

        self.root_directory_main = curation_dict[curation_dict['parent_dir']]
        self.todo_folder = curation_dict['folder_todo']
        self.underreview_folder = curation_dict['folder_underreview']
        self.reviewed_folder = curation_dict['folder_reviewed']
        self.published_folder = curation_dict['folder_published']
        self.rejected_folder = curation_dict['folder_rejected']

        self.stage_list = [self.todo_folder,
                           self.underreview_folder,
                           self.reviewed_folder,
                           self.published_folder]

    def get_source_stage(self, depositor_name, verbose=True):
        """
        Purpose:
          Retrieve source stage folder by searching for dataset on curation server

        :param depositor_name: Exact name of the data curation folder with spaces
        :param verbose: bool that warns source_path does not exist.  Default: True
               This is best used for new folders to avoid warning

        :return source_stage: str containing source stage name
        """

        source_path = glob(join(self.root_directory_main, '?.*', depositor_name))
        if len(source_path) == 0:
            err = f"Unable to find source_path for {depositor_name}"
            if verbose:
                self.log.warn(err)
            raise FileNotFoundError(err)
        if len(source_path) > 1:
            err = f"Multiple paths found for {depositor_name}"
            self.log.warn(err)
            self.log.debug(source_path)
            raise ValueError(err)
        if len(source_path) == 1:
            source_stage = source_path[0].replace(join(self.root_directory_main, ''), '').split('/')[0]

            return source_stage

    def main(self, depositor_name, source_stage, dest_stage):
        """
        Purpose:
          Move a data set on the curation server from one curation stage to another

        :param depositor_name: Exact name of the data curation folder with spaces
        :param source_stage: folder name either folder_todo, folder_underreview,
                             folder_reviewed, folder_published, or folder_rejected
        :param dest_stage: folder name either folder_todo, folder_underreview,
                           folder_reviewed, folder_published, or folder_rejected
        """

        # Define paths:
        source_path = join(self.root_directory_main, source_stage, depositor_name)
        # Strip out version folder convention for proper move with shutil.move
        dest_path = dirname(join(self.root_directory_main, dest_stage, depositor_name))

        # Move folder
        if exists(source_path):
            self.log.info(f"Moving: {depositor_name} from {source_stage} to ...")
            self.log.info(f" ... {dest_stage} on {self.root_directory_main}")
            if not exists(dest_path):
                self.log.info(f"Path does not exist! {dest_path}")
                self.log.info("Creating...")
                makedirs(dest_path)
                chmod(dest_path, 0o777)
            shutil.move(source_path, dest_path)
        else:
            self.log.info(f"WARNING: Unable to find source_path for {depositor_name}")

    def move_to_next(self, depositor_name, verbose=True):
        """
        Purpose:
          Perform move from one curation stage to the next

        :param depositor_name: Exact name of the data curation folder with spaces
        :param verbose: bool that warns source_path does not exist.  Default: True
        """

        try:
            # Get current path
            source_stage = self.get_source_stage(depositor_name, verbose=verbose)

            # Get destination path
            dest_stage_i = [i+1 for i in range(len(self.stage_list)) if
                            self.stage_list[i] == source_stage][0]
            dest_stage = self.stage_list[dest_stage_i]

            # Move folder
            self.main(depositor_name, source_stage, dest_stage)
        except FileNotFoundError:
            self.log.warn(f"Unable to find source_path for {depositor_name}")

    def move_back(self, depositor_name, verbose=True):
        """
        Purpose:
          Perform move from one curation stage back to previous one

        :param depositor_name: Exact name of the data curation folder with spaces
        :param verbose: bool that warns source_path does not exist.  Default: True
        """

        try:
            # Get current path
            source_stage = self.get_source_stage(depositor_name, verbose=verbose)

            # Get destination path
            dest_stage_i = [i-1 for i in range(len(self.stage_list)) if
                            self.stage_list[i] == source_stage][0]
            dest_stage = self.stage_list[dest_stage_i]

            # Move folder
            self.main(depositor_name, source_stage, dest_stage)
        except FileNotFoundError:
            self.log.warn(f"Unable to find source_path for {depositor_name}")

    def reject(self, depositor_name, verbose=True):
        """
        Purpose:
          Perform move from current stage to rejection stage

        :param depositor_name: Exact name of the data curation folder with spaces
        :param verbose: bool that warns source_path does not exist.  Default: True
        """

        try:
            # Get current path
            source_stage = self.get_source_stage(depositor_name, verbose=verbose)

            # Move folder to reject
            self.main(depositor_name, source_stage, self.rejected_folder)
        except FileNotFoundError:
            self.log.warn(f"Unable to find source_path for {depositor_name}")
