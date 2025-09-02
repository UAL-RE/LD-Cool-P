"""
A set of functions to change permissions for a given path or file for data
curation backend support
"""

from os.path import join, isdir, isfile

from os import chmod, walk


def curation(path, mode=0o770):
    """
    Purpose:
      Set permissions for all folders and files under the
      parent location of [path]

    :param path: Parent location path
    :param mode: Mode. Default is rwx with '0o770'
    """

    if isdir(path) or isfile(path):
        chmod(path, mode)

    for dir_path, dir_names, files in walk(path):
        for dir_name in dir_names:
            chmod(join(dir_path, dir_name), mode)

        for file in files:
            chmod(join(dir_path, file), mode)
