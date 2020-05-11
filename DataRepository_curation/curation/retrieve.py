import os
from os.path import exists
import configparser
from urllib.request import Request, urlopen

from figshare.figshare import Figshare  # , issue_request
from ..admin import permissions

# from ..figshare_api import FigshareInstituteAdmin

# Read in default configuration file
config = configparser.ConfigParser()
config.read('DataRepository_curation/config/default.ini')

api_token = config.get('global', 'api_token')

# fs_admin = FigshareInstituteAdmin(token=api_token)


def private_file_retrieve(url, filename=None, token=None):

    req = Request(url)
    if token:
        req.add_header('Authorization', 'token {}'.format(token))

    response = urlopen(req)
    content = response.read()
    print(url)

    f = open(filename, 'wb')
    f.write(content)
    f.close()


def download_files(article_id, fs=None, root_directory=None, data_directory=None):

    if root_directory is None:
        root_directory = os.getcwd()

    if not fs:
        if api_token is None or api_token == "***override***":
            print("ERROR: api_token not available from config file")
            api_token = input("Provide token through prompt : ")

        fs = Figshare(token=api_token, private=True)

    # Retrieve article information
    # article_details = fs.get_article_details(article_id)

    file_list = fs.list_files(article_id)
    n_files = len(file_list)

    if not data_directory:
        dir_path = os.path.join(root_directory, "figshare_{0}/".format(article_id))
    else:
        dir_path = os.path.join(root_directory, data_directory)

    os.makedirs(dir_path, exist_ok=True)  # This might require Python >=3.2

    print("Total number of files: {}".format(n_files))

    for n, file_dict in zip(range(n_files), file_list):
        print("Retrieving {} of {} : {}".format(n+1, n_files, file_dict['name']))
        filename = os.path.join(dir_path, file_dict['name'])
        if not exists(filename):
            private_file_retrieve(file_dict['download_url'], filename=filename,
                                  token=api_token)
        else:
            print("File exists! Not overwriting!")

    # Change permissions on folders and files
    permissions.curation(dir_path)
