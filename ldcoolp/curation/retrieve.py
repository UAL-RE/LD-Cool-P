import os
from os.path import exists

from urllib.request import Request, urlopen, build_opener, install_opener, urlretrieve

from figshare.figshare import Figshare  # , issue_request
from ldcoolp.admin import permissions

from ..config import api_token


def private_file_retrieve(url, filename=None, token=None, url_open=False):
    """
    Purpose:
      Custom Request to privately retrieve a file with a token.
      This was built off of the figshare Python code, but a urlretrieve
      did not handle providing a token in the header.

    :param url: Full URL (str)
    :param filename: Full filename for file to be written (str)
    :param token: API token (str)
    :param url_open: Boolean to indicate whether to use urlopen. Default: False
    """

    if not url_open:
        if token:
            opener = build_opener()
            opener.addheaders = [('Authorization', 'token {}'.format(token))]
            install_opener(opener)
        urlretrieve(url, filename)
    else:
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
                   url_open=False):
    """
    Purpose:
      Retrieve data for a Figshare deposit following data curation workflow

    :param article_id: Figshare article ID (int)
    :param fs: Figshare object
    :param root_directory: Root path for curation workflow (str)
    :param data_directory: Relative folder path for primary location of data (str)
    :param url_open: bool indicates using urlopen over urlretrieve. Default: False
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
                                  token=fs.token, url_open=url_open)
        else:
            print("File exists! Not overwriting!")

    # Change permissions on folders and files
    # permissions.curation(dir_path)
    permissions.curation(dir_path, mode=0o555)  # read and execute only
