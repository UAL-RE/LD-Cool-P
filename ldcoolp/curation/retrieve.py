import shutil
import os
from os.path import exists
import glob

from urllib.request import Request, urlopen

from figshare.figshare import Figshare  # , issue_request
from ldcoolp.admin import permissions

from ..config import api_token
from ..config import readme_template


def private_file_retrieve(url, filename=None, token=None):
    """
    Purpose:
      Custom Request to privately retrieve a file with a token.
      This was built off of the figshare Python code, but a urlretrieve
      did not handle providing a token in the header.

    :param url: Full URL (str)
    :param filename: Full filename for file to be written (str)
    :param token: API token (str)
    """

    req = Request(url)
    if token:
        req.add_header('Authorization', 'token {}'.format(token))

    response = urlopen(req)
    content = response.read()
    print(url)

    f = open(filename, 'wb')
    f.write(content)
    f.close()


def download_files(article_id, fs=None, root_directory=None, data_directory=None,
                   copy_directory=None, readme_copy=False):
    """
    Purpose:
      Retrieve data for a Figshare deposit following data curation workflow

    :param article_id: Figshare article ID (int)
    :param fs: Figshare object
    :param root_directory: Root path for curation workflow (str)
    :param data_directory: Relative folder path for primary location of data (str)
    :param copy_directory: Relative folder path for secondary location of data (str)
    :param readme_copy: Bool to indicate whether to copy README files into [copy_directory]
    """
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
    permissions.curation(dir_path)

    print("Total number of files: {}".format(n_files))

    for n, file_dict in zip(range(n_files), file_list):
        print("Retrieving {} of {} : {}".format(n+1, n_files, file_dict['name']))
        filename = os.path.join(dir_path, file_dict['name'])
        if not exists(filename):
            private_file_retrieve(file_dict['download_url'], filename=filename,
                                  token=fs.token)
        else:
            print("File exists! Not overwriting!")

    # Change permissions on folders and files
    if not readme_copy:
        permissions.curation(dir_path)
    else:
        permissions.curation(dir_path, mode=0o555)  # read and execute only

        # Save a copy of README files
        if copy_directory:
            print("Saving a copy in {}".format(copy_directory))

            # Create [copy_path] location
            copy_path = os.path.join(root_directory, copy_directory)
            os.makedirs(copy_path, exist_ok=True)

            README_files = glob.glob(os.path.join(dir_path, 'README*.txt')) + \
                           glob.glob(os.path.join(dir_path, 'README*.md'))
            if len(README_files) != 0:
                for r_file in README_files:
                    print("Saving a copy of : {}".format(r_file))
                    shutil.copy(r_file, copy_path)

                if len(README_files) == 1:
                    print("Only one README file found!")
                    print("Renaming to README_template.md")

                    src_rename = os.path.join(copy_path,
                                              os.path.basename(README_files[0]))
                    dst_rename = os.path.join(copy_path, readme_template)
                    os.rename(src_rename, dst_rename)
                else:
                    print("More than one README file found!")
                    print("Manual intervention needed ...")
                    print(f"Select and save a README file in {copy_path} as {readme_template}")
                    input("Hit ENTER when ready to proceed ...")
            else:
                print("No README files found.")
                print(f"Note: default {readme_template} will be used")

            permissions.curation(copy_path)  # rwx permissions
        else:
            print("Not saving a copy in {}".format(copy_directory))
