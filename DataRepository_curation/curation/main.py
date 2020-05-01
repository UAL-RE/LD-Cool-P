import configparser
from os.path import join

from .retrieve import download_files
from ..admin import move, permissions
from .reports import review_report

# Read in default configuration file
config = configparser.ConfigParser()
config.read('DataRepository_curation/config/default.ini')

source = config.get('curation', 'source')
root_directory0 = config.get('curation', '{}_path'.format(source))

folder_todo = config.get('curation', 'folder_todo')
folder_data = config.get('curation', 'folder_data')

root_directory = join(root_directory0, folder_todo)

api_token = config.get('global', 'api_token')


def workflow(article_id):
    """
    Purpose:
      This function follows our initial set-up to:
       1. Retrieve the data for a given deposit
       2. Set permissions and ownership (the latter needs to be tested and performed)
       3. Download curatorial review report
       4. Check the README file

    :param article_id:
    :return:
    """
    # Retrieve data and place in 1.ToDo curation folder
    depositor_name = '' # This need to be determined using figshare metadata
    data_directory = join(depositor_name, folder_data)
    download_files(article_id, root_directory=root_directory,
                   data_directory=data_directory)

    # Download curation report
    review_report(depositor_name)

    # Move to next curation stage
    move.move_to_next(depositor_name)

    # Check for README file
