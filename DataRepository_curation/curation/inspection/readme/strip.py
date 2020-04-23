from os.path import exists, join
from os import walk
import shutil
from urllib.request import urlretrieve

import numpy as np

from ...admin import permissions

import configparser

config = configparser.ConfigParser()
config.read('DataRepository_curation/config/default.ini')

folder_data = config.get('curation', 'folder_data')

source = config.get('curation', 'source')
root_directory = config.get('curation', '{}_path'.format(source))

underreview_folder = config.get('curation', 'folder_underreview')

staging_directory = join(root_directory, underreview_folder)

readme_url = config.get('curation', 'readme_url')


def default_readme_path(depositor_name):
    """
    Purpose:
      Provide full path for default README.txt file and data_path

    :param depositor_name: Exact name of the data curation folder with spaces

    :return README_file_default: str containing full path
    :return data_path: full path to DATA folder
    """

    data_path = join(staging_directory, depositor_name, folder_data)

    README_file_default = join(data_path, 'README.txt')
    return README_file_default, data_path


def walkthrough(data_path, ignore=''):
    """
    Purpose:
      Perform walkthrough to find other README files

    :param data_path: path to DATA folder
    :param ignore: full path of default README.txt to ignore
    :return:
    """
    for dir_path, dir_names, files in walk(data_path):
        for file in files:
            if 'README' in file.upper():  # case insensitive
                file_fullname = join(dir_path, file)
                if file_fullname != ignore:
                    print("File exists : {}".format(file_fullname))


def check_exists(depositor_name):
    """
    Purpose:
      Check that a README file exists

    :param depositor_name: Exact name of the data curation folder with spaces
    :return: Will raise error
    """

    README_file_default, data_path = default_readme_path(depositor_name)

    if exists(README_file_default):
        print("Default README.txt file exists!!!")

        print("Checking for additional README files")
        walkthrough(data_path, ignore=README_file_default)
    else:
        print("Default README.txt file DOES NOT exist!!!")
        print("Searching other possible locations...")

        walkthrough(data_path)


def retrieve(depositor_name):
    """
    Purpose:
      Retrieve template of README.txt file if such file is not present

    :param depositor_name: Exact name of the data curation folder with spaces
    :return: Download files and place it within the [folder_data] path
    """

    README_file_default, _ = default_readme_path(depositor_name)

    if not exists(README_file_default):
        print("Retrieving README template...")
        urlretrieve(readme_url, README_file_default)
        permissions.curation(README_file_default)
    else:
        print("Default README file found! Not overwriting with template!")


def strip_html_comments(lines0, change):
    """
    Purpose:
      Remove HTML comments from README.txt file

    :param lines0: list containing text from open()
    :param change: int that indicates whether changes have been implemented

    :return lines: list containing text with HTML comments stripped out
    :return change: Updated change (+1) if changes are made
    """

    # Strip out HTML comments noted via <!--- to -->
    html_comment_beg = [xx for xx in range(len(lines0)) if '<!---' in lines0[xx][0:5]]
    html_comment_end = [xx for xx in range(len(lines0)) if '-->' in lines0[xx][0:3]]

    if len(html_comment_beg) != 0:
        change += 1

    list_range = [[*range(beg, end+1)] for beg, end in zip(html_comment_beg, html_comment_end)]

    # Concentage list_range into a single list of index to remove
    remove_index = [j for i in list_range for j in i]

    # Easier to use numpy to remove a list of index than using list remove()
    lines = np.array(lines0)
    lines = np.delete(lines, remove_index)

    return lines, change


def strip_comments(depositor_name):

    README_file_default, _ = default_readme_path(depositor_name)

    f1 = open(README_file_default, 'r')
    lines0 = f1.readlines()
    f1.close()

    change = 0

    lines, change = strip_html_comments(lines0, change)

    if change:
        print(README_file_default)
        shutil.copy(README_file_default, README_file_default.replace('.txt', '.orig.txt'))

        f2 = open(README_file_default, 'w')
        f2.writelines(lines)
        f2.close()
