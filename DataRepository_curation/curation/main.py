import configparser
from os.path import join

from .retrieve import download_files
from ..admin import move, permissions
from .reports import review_report
from figshare.figshare import Figshare
from ..figshare_api import FigshareInstituteAdmin

# Read in default configuration file
config = configparser.ConfigParser()
config.read('DataRepository_curation/config/default.ini')

source = config.get('curation', 'source')
root_directory0 = config.get('curation', '{}_path'.format(source))

folder_todo = config.get('curation', 'folder_todo')
folder_data = config.get('curation', 'folder_data')

root_directory = join(root_directory0, folder_todo)

api_token = config.get('global', 'api_token')

fs = Figshare(token=api_token, private=True)
fs_admin = FigshareInstituteAdmin(token=api_token)


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

    # Retrieve info about deposit:
    cur_df = fs_admin.get_curation_list()
    acct_df = fs_admin.get_account_list()

    cur_loc_dict = cur_df.loc[cur_df['article_id'] == article_id].reset_index().\
        to_dict(orient='records')[0]
    curation_dict = fs_admin.get_curation_details(cur_loc_dict['id'])
    account_id = curation_dict['account_id']
    depositor_dict = acct_df.loc[acct_df['id'] == account_id].reset_index().\
        to_dict(orient='records')[0]

    # Retrieve data and place in 1.ToDo curation folder
    depositor_surname = depositor_dict['last_name']
    depositor_first = depositor_dict['first_name'].split(' ')[0]
    depositor_name = "{} {}".format(depositor_first, depositor_surname)
    data_directory = join(depositor_name, folder_data)
    download_files(article_id, root_directory=root_directory,
                   data_directory=data_directory)

    # Download curation report
    review_report(depositor_name)

    # Move to next curation stage
    move.move_to_next(depositor_name)

    # Check for README file
