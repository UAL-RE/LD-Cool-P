"""
A set of functions to change permissions for a given path or file for data
curation backend support
"""

from os.path import join, isdir, isfile

from os import chmod, walk


def curation(path):
    """
    Purpose:
      Set permissions to rwx for all folders and files under the
      parent location of [path]

    :param path: Parent location path
    """

    if isdir(path) or isfile(path):
        chmod(path, 0o777)

    for dir_path, dir_names, files in walk(path):
        for dir_name in dir_names:
            chmod(join(dir_path, dir_name), 0o777)

        for file in files:
            chmod(join(dir_path, file), 0o777)
