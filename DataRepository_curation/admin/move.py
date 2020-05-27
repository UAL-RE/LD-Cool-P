from os.path import join, dirname
import shutil
from glob import glob

from DataRepository_curation import config_file

import configparser

# Read in default configuration file
config = configparser.ConfigParser()
config.read(config_file)

source = config.get('curation', 'source')
root_directory = config.get('curation', '{}_path'.format(source))

folder_todo = config.get('curation', 'folder_todo')
folder_underreview = config.get('curation', 'folder_underreview')
folder_reviewed = config.get('curation', 'folder_reviewed')
folder_published = config.get('curation', 'folder_published')
folder_rejected = config.get('curation', 'folder_rejected')

stage_list = [folder_todo, folder_underreview, folder_reviewed, folder_published]


def get_source_stage(depositor_name):
    """
    Purpose:
      Retrieve source stage folder by searching for dataset on curation server

    :param depositor_name: : Exact name of the data curation folder with spaces
    :return source_stage: str containing source stage name
    """

    source_path = glob(join(root_directory, '*', depositor_name))[0]
    source_stage = dirname(source_path.replace(join(root_directory, ''), ''))

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
    source_path = join(root_directory, source_stage, depositor_name)
    dest_path = join(root_directory, dest_stage, depositor_name)

    # Move folder
    print("Moving: {} from {} to ...".format(depositor_name, source_stage))
    print(" ... {} on {}".format(dest_stage, root_directory))
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
    main(depositor_name, source_stage, folder_rejected)
