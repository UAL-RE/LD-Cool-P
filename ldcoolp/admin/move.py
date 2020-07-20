from os.path import join, dirname
import shutil
from glob import glob

# Read in default configuration settings
from ..config import root_directory_main
from ..config import todo_folder, underreview_folder, reviewed_folder, \
    published_folder, rejected_folder

stage_list = [todo_folder, underreview_folder, reviewed_folder, published_folder]


def get_source_stage(depositor_name):
    """
    Purpose:
      Retrieve source stage folder by searching for dataset on curation server

    :param depositor_name: : Exact name of the data curation folder with spaces
    :return source_stage: str containing source stage name
    """

    source_path = glob(join(root_directory_main, '?.*', depositor_name))
    if len(source_path) == 0:
        raise FileNotFoundError(f"Unable to find source_path for {depositor_name}")
    if len(source_path) > 1:
        print(source_path)
        raise ValueError(f"Multiple paths found for {depositor_name}")
    if len(source_path) == 1:
        source_stage = dirname(source_path[0].replace(join(root_directory_main, ''), ''))

        return source_stage


def main(depositor_name, source_stage, dest_stage):
    """
    Purpose:
      Move a data set on the curation server from one curation stage to another

    :param depositor_name: Exact name of the data curation folder with spaces
    :param source_stage: folder name either folder_todo, folder_underreview,
                         folder_reviewed, folder_published, or folder_rejected
    :param dest_stage: folder name either folder_todo, folder_underreview,
                       folder_reviewed, folder_published, or folder_rejected
    """

    # Define path:
    source_path = join(root_directory_main, source_stage, depositor_name)
    dest_path = join(root_directory_main, dest_stage, depositor_name)

    # Move folder
    print("Moving: {} from {} to ...".format(depositor_name, source_stage))
    print(" ... {} on {}".format(dest_stage, root_directory_main))
    shutil.move(source_path, dest_path)


def move_to_next(depositor_name):
    """
    Purpose:
      Perform move from one curation stage to the next

    :param depositor_name: Exact name of the data curation folder with spaces
    """

    # Get current path
    source_stage = get_source_stage(depositor_name)

    # Get destination path
    dest_stage_i = [i+1 for i in range(len(stage_list)) if
                    stage_list[i] == source_stage][0]
    dest_stage = stage_list[dest_stage_i]

    # Move folder
    main(depositor_name, source_stage, dest_stage)


def reject(depositor_name):
    """
    Purpose:
      Perform move from current stage to rejection stage

    :param depositor_name: Exact name of the data curation folder with spaces
    """
    # Get current path
    source_stage = get_source_stage(depositor_name)

    # Move folder to reject
    main(depositor_name, source_stage, rejected_folder)
