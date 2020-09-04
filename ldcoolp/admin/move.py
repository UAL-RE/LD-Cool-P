from os.path import join, dirname, exists
import shutil
from glob import glob

# Read in default configuration settings
from ..config import config_default_dict


class MoveClass:

    def __init__(self, curation_dict=config_default_dict['curation']):

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

    def get_source_stage(self, depositor_name):
        """
        Purpose:
          Retrieve source stage folder by searching for dataset on curation server

        :param depositor_name: : Exact name of the data curation folder with spaces
        :return source_stage: str containing source stage name
        """

        source_path = glob(join(self.root_directory_main, '?.*', depositor_name))
        if len(source_path) == 0:
            raise FileNotFoundError(f"Unable to find source_path for {depositor_name}")
        if len(source_path) > 1:
            print(source_path)
            raise ValueError(f"Multiple paths found for {depositor_name}")
        if len(source_path) == 1:
            source_stage = dirname(source_path[0].replace(join(self.root_directory_main, ''), ''))

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
        dest_path = join(self.root_directory_main, dest_stage, depositor_name)

        # Move folder
        if exists(source_path):
            print(f"Moving: {depositor_name} from {source_stage} to ...")
            print(f" ... {dest_stage} on {self.root_directory_main}")
            shutil.move(source_path, dest_path)
        else:
            print(f"WARNING: Unable to find source_path for {depositor_name}")

    def move_to_next(self, depositor_name):
        """
        Purpose:
          Perform move from one curation stage to the next

        :param depositor_name: Exact name of the data curation folder with spaces
        """

        try:
            # Get current path
            source_stage = self.get_source_stage(depositor_name)

            # Get destination path
            dest_stage_i = [i+1 for i in range(len(self.stage_list)) if
                            self.stage_list[i] == source_stage][0]
            dest_stage = self.stage_list[dest_stage_i]

            # Move folder
            self.main(depositor_name, source_stage, dest_stage)
        except FileNotFoundError:
            print(f"WARNING: Unable to find source_path for {depositor_name}")

    def reject(self, depositor_name):
        """
        Purpose:
          Perform move from current stage to rejection stage

        :param depositor_name: Exact name of the data curation folder with spaces
        """

        try:
            # Get current path
            source_stage = self.get_source_stage(depositor_name)

            # Move folder to reject
            self.main(depositor_name, source_stage, self.rejected_folder)
        except FileNotFoundError:
            print(f"WARNING: Unable to find source_path for {depositor_name}")
