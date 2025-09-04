"""
A set of functions to change permissions for a given path or file for data
curation backend support
"""

from os.path import join, isdir, isfile

from os import chmod, walk


def curation(path, folder_mode=0o2770, file_mode=0o2660):
    """
    Purpose:
      Set permissions for all folders and files under the
      parent location of [path]

    :param path: Parent location path
    :param folder_mode: Mode for folders. Default is rwx with '0o770'
    :param file_mode: Mode for files. Default is rw- with '660'
    """

    if isdir(path):
        chmod(path, folder_mode)

    if isfile(path):
        chmod(path, file_mode)

    for dir_path, dir_names, files in walk(path):
        for dir_name in dir_names:
            chmod(join(dir_path, dir_name), folder_mode)

        for file in files:
            chmod(join(dir_path, file), file_mode)
