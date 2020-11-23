import os
from os.path import exists

from urllib.request import Request, urlopen, build_opener, install_opener, urlretrieve

from ldcoolp.admin import permissions

# Logging
from ldcoolp.logger import log_stdout


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
            opener.addheaders = [('Authorization', f'token {token}')]
            install_opener(opener)
        urlretrieve(url, filename)
    else:
        req = Request(url)
        if token:
            req.add_header('Authorization', f'token {token}')

        response = urlopen(req)
        content = response.read()
        print(url)

        f = open(filename, 'wb')
        f.write(content)
        f.close()


def download_files(article_id, fs, root_directory=None, data_directory=None,
                   log=None, url_open=False):
    """
    Purpose:
      Retrieve data for a Figshare deposit following data curation workflow

    :param article_id: Figshare article ID (int)
    :param fs: Figshare object
    :param root_directory: Root path for curation workflow (str)
    :param data_directory: Relative folder path for primary location of data (str)
    :param log: logger.LogClass object. Default is stdout via python logging
    :param url_open: bool indicates using urlopen over urlretrieve. Default: False
    """

    if isinstance(log, type(None)):
        log = log_stdout()

    if root_directory is None:
        root_directory = os.getcwd()

    # Retrieve article information
    # article_details = fs.get_article_details(article_id)

    file_list = fs.list_files(article_id)
    n_files = len(file_list)

    if not data_directory:
        dir_path = os.path.join(root_directory, f"figshare_{article_id}/")
    else:
        dir_path = os.path.join(root_directory, data_directory)

    os.makedirs(dir_path, exist_ok=True)  # This might require Python >=3.2
    permissions.curation(dir_path)

    log.info(f"Total number of files: {n_files}")

    for n, file_dict in zip(range(n_files), file_list):
        log.info(f"Retrieving {n+1} of {n_files} : {file_dict['name']} ({file_dict['size']})")
        log.info(f"URL: {file_dict['download_url']}")
        filename = os.path.join(dir_path, file_dict['name'])
        if not exists(filename):
            private_file_retrieve(file_dict['download_url'], filename=filename,
                                  token=fs.token, url_open=url_open)
        else:
            log.info("File exists! Not overwriting!")

    # Change permissions on folders and files
    # permissions.curation(dir_path)
    permissions.curation(dir_path, mode=0o555)  # read and execute only
