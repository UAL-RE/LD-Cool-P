import os
import shutil
from os.path import exists
from os import chmod
import requests
from requests import HTTPError

from ldcoolp.admin import permissions

# Logging
from redata.commons.logger import log_stdout

# Metadata
from .inspection.checksum import check_md5
from .metadata import save_metadata

N_TRIES_MD5 = 3  # Number of attempts for checksum


def private_file_retrieve(url, filename=None, token=None, log=None):
    """
    Purpose:
      Custom Request to privately retrieve a file with a token.
      This was built off of the figshare Python code, but a urlretrieve
      did not handle providing a token in the header.

    :param url: Full URL (str)
    :param filename: Full filename for file to be written (str)
    :param token: API token (str)
    :param log: logger.LogClass object. Default is stdout via python logging
    """

    if isinstance(log, type(None)):
        log = log_stdout()

    headers = dict()
    if token:
        headers['Authorization'] = f'token {token}'

    try:
        h = requests.head(url, headers=headers)
        h.raise_for_status()

        # Chunk read and write with stream option and copyfileobj
        with requests.get(url, stream=True, headers=headers) as r:
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
    except (HTTPError, IOError) as error:
        log.warning(error)
        raise HTTPError(error)


def download_files(article_id, fs, root_directory=None, data_directory=None,
                   metadata_directory=None, log=None,
                   metadata_only=False):
    """
    Purpose:
      Retrieve data for a Figshare deposit following data curation workflow

    :param article_id: Figshare article ID (int)
    :param fs: Figshare object
    :param root_directory: Root path for curation workflow (str)
    :param data_directory: Relative folder path for primary location of data (str)
    :param metadata_directory: Relative folder path for primary location of metadata (str)
    :param log: logger.LogClass object. Default is stdout via python logging
    :param metadata_only: bool indicates whether to retrieve metadata. Default: True
           If set, no files are downloaded
    """

    if isinstance(log, type(None)):
        log = log_stdout()

    log.info("")
    if metadata_only:
        log.info(f"** NO FILE RETRIEVAL: metadata_only={metadata_only} **")
    else:
        log.info("** DOWNLOADING DATA **")

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

    out_file_prefix = f"file_list_original_{article_id}"
    save_metadata(file_list, out_file_prefix, root_directory=root_directory,
                  metadata_directory=metadata_directory, save_csv=True,
                  log=log)

    if not metadata_only:
        for n, file_dict in zip(range(n_files), file_list):
            log.info(f"Retrieving {n+1} of {n_files} : "
                     f"{file_dict['name']} ({file_dict['size']})")
            log.info(f"URL: {file_dict['download_url']}")
            filename = os.path.join(dir_path, file_dict['name'])
            retrieve_cnt = 0
            checksum_flag = False
            if not exists(filename):
                while retrieve_cnt < N_TRIES_MD5:
                    log.info(f"Retrieval attempt #{retrieve_cnt + 1}")
                    try:
                        private_file_retrieve(file_dict['download_url'],
                                              filename=filename, token=fs.token,
                                              log=log)
                        log.info("Download successful!")
                        retrieve_cnt += 1
                    except (HTTPError, IOError):
                        retrieve_cnt += 1

                    # Perform checksum
                    if exists(filename):
                        if not file_dict['is_link_only']:
                            checksum_flag = check_md5(filename,
                                                      file_dict['supplied_md5'])
                            if checksum_flag:
                                chmod(filename, 0o2440)
                                break
                        else:
                            log.info("Not performing checksum on linked-only record")
                            break
                else:
                    if not checksum_flag:
                        log.warning("File retrieval unsuccessful! "
                                    f"Aborted after {N_TRIES_MD5} tries")
            else:
                log.info("File exists! Not overwriting!")

    # Change permissions on folders and files
    permissions.curation(dir_path, folder_mode=0o2550, file_mode=0o2440)  # read and execute only
