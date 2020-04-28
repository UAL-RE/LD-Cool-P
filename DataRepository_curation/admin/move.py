from os.path import join
import shutil

import configparser

# Read in default configuration file
config = configparser.ConfigParser()
config.read('DataRepository_curation/config/default.ini')

source = config.get('curation', 'source')
root_directory = config.get('curation', '{}_path'.format(source))

folder_todo = config.get('curation', 'folder_todo')
folder_underreview = config.get('curation', 'folder_underreview')
folder_reviewed = config.get('curation', 'folder_reviewed')
folder_published = config.get('curation', 'folder_published')
folder_rejected = config.get('curation', 'folder_rejected')


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

    print("Moving: {} from {} to {}".format(depositor_name, source_path, dest_path))
    shutil.move(source_path, dest_path)
