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

acct_df = fs_admin.get_account_list()


def df_to_dict_single(df):
    """
    Purpose:
      Convert a single entry pandas DataFrame into a dictionary and strip out
      indexing information

    :param df: pandas DataFrame with single entry (e.g., use df.loc[] to filter)

    :return df_dict: dict that contains single entry pandas DF
    """
    df_dict = df.reset_index().to_dict(orient='records')[0]
    return df_dict


def get_depositor_name(article_id, cur_df):

    print("Retrieving depositor_name for {} ... ".format(article_id))

    cur_loc_dict = df_to_dict_single(cur_df.loc[cur_df['article_id'] == article_id])
    curation_dict = fs_admin.get_curation_details(cur_loc_dict['id'])
    account_id = curation_dict['account_id']
    depositor_dict = df_to_dict_single(acct_df.loc[acct_df['id'] == account_id])

    depositor_surname = depositor_dict['last_name']  # full last name
    depositor_first = depositor_dict['first_name']  # full first name
    depositor_fullname = "{} {}".format(depositor_first, depositor_surname)
    depositor_dispname = "{} {}".format(depositor_first.split(' ')[0], depositor_surname)

    # Check to see if the depositor is in the list of authors
    authors = [d['full_name'] for d in curation_dict['item']['authors']]
    if depositor_fullname in authors or depositor_dispname in authors:
        print("  Depositor == author")
        depositor_name = depositor_dispname
    else:
        print("  Depositor != author")
        depositor_name = '{} - {}'.format(depositor_dispname, authors[0])
    print("depository_name : {}".format(depositor_name))

    return depositor_name


def workflow(article_id):
    """
    Purpose:
      This function follows our initial set-up to:
       1. Retrieve the data for a given deposit
       2. Set permissions and ownership (the latter needs to be tested and performed)
       3. Download curatorial review report
       4. Download Qualtrics Deposit Agreement form
       5. Check the README file

    :param article_id:
    :return:
    """

    # Retrieve info about deposit:
    cur_df = fs_admin.get_curation_list()

    # Retrieve depositor name
    depositor_name = get_depositor_name(article_id, cur_df)

    # Retrieve data and place in 1.ToDo curation folder
    data_directory = join(depositor_name, folder_data)
    download_files(article_id, root_directory=root_directory,
                   data_directory=data_directory)

    # Download curation report
    review_report(depositor_name)

    # Placeholder to download Qualtrics deposit agreement form

    # Move to next curation stage
    move.move_to_next(depositor_name)

    # Check for README file
