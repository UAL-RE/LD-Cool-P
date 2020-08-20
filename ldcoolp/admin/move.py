from os.path import join, dirname, exists
import shutil
from glob import glob

# Logging
from ..logger import log_stdout

# Read in default configuration settings
from ..config import root_directory_main
from ..config import todo_folder, underreview_folder, reviewed_folder, \
    published_folder, rejected_folder

stage_list = [todo_folder, underreview_folder, reviewed_folder, published_folder]


def get_source_stage(depositor_name, log=None):
    """
    Purpose:
      Retrieve source stage folder by searching for dataset on curation server

    :param depositor_name: Exact name of the data curation folder with spaces
    :param log: logger.LogClass object. Default is stdout via python logging

    :return source_stage: str containing source stage name
    """

    if isinstance(log, type(None)):
        log = log_stdout()

    source_path = glob(join(root_directory_main, '?.*', depositor_name))
    if len(source_path) == 0:
        err = f"Unable to find source_path for {depositor_name}"
        log.warn(err)
        raise FileNotFoundError(err)
    if len(source_path) > 1:
        err = f"Multiple paths found for {depositor_name}"
        log.warn(err)
        log.debug(source_path)
        raise ValueError(err)
    if len(source_path) == 1:
        source_stage = dirname(source_path[0].replace(join(root_directory_main, ''), ''))

        return source_stage


def main(depositor_name, source_stage, dest_stage, log=None):
    """
    Purpose:
      Move a data set on the curation server from one curation stage to another

    :param depositor_name: Exact name of the data curation folder with spaces
    :param source_stage: folder name either folder_todo, folder_underreview,
                         folder_reviewed, folder_published, or folder_rejected
    :param dest_stage: folder name either folder_todo, folder_underreview,
                       folder_reviewed, folder_published, or folder_rejected
    :param log: logger.LogClass object. Default is stdout via python logging
    """

    if isinstance(log, type(None)):
        log = log_stdout()

    # Define paths:
    source_path = join(root_directory_main, source_stage, depositor_name)
    dest_path = join(root_directory_main, dest_stage, depositor_name)

    # Move folder
    if exists(source_path):
        log.info(f"Moving: {depositor_name} from {source_stage} to ...")
        log.info(f" ... {dest_stage} on {root_directory_main}")
        shutil.move(source_path, dest_path)
    else:
        log.info(f"WARNING: Unable to find source_path for {depositor_name}")


def move_to_next(depositor_name, log=None):
    """
    Purpose:
      Perform move from one curation stage to the next

    :param depositor_name: Exact name of the data curation folder with spaces
    :param log: logger.LogClass object. Default is stdout via python logging
    """

    if isinstance(log, type(None)):
        log = log_stdout()

    try:
        # Get current path
        source_stage = get_source_stage(depositor_name, log=log)

        # Get destination path
        dest_stage_i = [i+1 for i in range(len(stage_list)) if
                        stage_list[i] == source_stage][0]
        dest_stage = stage_list[dest_stage_i]

        # Move folder
        main(depositor_name, source_stage, dest_stage, log=log)
    except FileNotFoundError:
        log.warn(f"Unable to find source_path for {depositor_name}")


def reject(depositor_name, log=None):
    """
    Purpose:
      Perform move from current stage to rejection stage

    :param depositor_name: Exact name of the data curation folder with spaces
    :param log: logger.LogClass object. Default is stdout via python logging
    """

    if isinstance(log, type(None)):
        log = log_stdout()

    try:
        # Get current path
        source_stage = get_source_stage(depositor_name, log=log)

        # Move folder to reject
        main(depositor_name, source_stage, rejected_folder, log=log)
    except FileNotFoundError:
        log.warn(f"Unable to find source_path for {depositor_name}")
