import configparser
from os.path import join

# Admin
from ..admin import move, permissions

# Curation
from . import df_to_dict_single
from .retrieve import download_files
from .reports import review_report

# API
from figshare.figshare import Figshare
from ..figshare_api import FigshareInstituteAdmin
from .api.qualtrics import Qualtrics

# Read in default configuration file
config = configparser.ConfigParser()
config.read('DataRepository_curation/config/default.ini')

source = config.get('curation', 'source')
root_directory0 = config.get('curation', '{}_path'.format(source))

folder_todo = config.get('curation', 'folder_todo')
folder_data = config.get('curation', 'folder_data')

root_directory = join(root_directory0, folder_todo)

api_token = config.get('global', 'api_token')
if api_token is None or api_token == "***override***":
    print("ERROR: figshare api_token not available from config file")
    api_token = input("Provide figshare token through prompt : ")

fs = Figshare(token=api_token, private=True)
fs_admin = FigshareInstituteAdmin(token=api_token)

acct_df = fs_admin.get_account_list()

qualtrics_survey_id = config.get('curation', 'qualtrics_survey_id')
if qualtrics_survey_id is None or qualtrics_survey_id == "***override***":
    qualtrics_survey_id = input("Provide Qualtrics Survey ID through prompt : ")

qualtrics_token = config.get('curation', 'qualtrics_token')
if qualtrics_token is None or qualtrics_token == "***override***":
    qualtrics_token = input("Provide Qualtrics API token through prompt : ")

qualtrics_dataCenter = config.get('curation', 'qualtrics_dataCenter')
if qualtrics_dataCenter is None or qualtrics_dataCenter == "***override***":
    qualtrics_dataCenter = input("Provide Qualtrics dataCenter through prompt : ")


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
    download_files(article_id, fs=fs, root_directory=root_directory,
                   data_directory=data_directory)

    # Download curation report
    review_report(depositor_name)

    # Placeholder to download Qualtrics deposit agreement form
    q = Qualtrics(qualtrics_dataCenter, qualtrics_token, qualtrics_survey_id)
    try:
        ResponseID = q.find_deposit_agreement(depositor_name)
        print("Qualtrics ResponseID : {}".format(ResponseID))
    except ValueError:
        print("Unable to obtain a unique match")

    # Move to next curation stage
    move.move_to_next(depositor_name)

    # Placeholder to check for README file and create one if it doesn't exists

