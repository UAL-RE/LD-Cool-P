"""
A set of functions to change permissions for a given path or file for data
curation backend support
"""

from os.path import join, isdir

from os import chmod, chown, walk


def curation(path):
    """
    Purpose:
      Set permissions to rwx for all folders and files under the
      parent location of [path]

    :param path: Parent location path
    """

    if isdir(path):
        chmod(path, 0o777)

    for dir_path, dir_names, files in walk(path):
        for dir_name in dir_names:
            # print(join(root, file))
            chmod(join(dir_path, dir_name), 0o777)

        for file in files:
            # print(join(root, file))
            chmod(join(dir_path, file), 0o777)


def curation_owner(path, user):
    """
    Purpose:
      Change user and group ownership of all folders and files
      under the parent location of [path]

    :param path: Parent location path
    """

    group = ''  # Placeholder

    if isdir(path):
        chown(path, user, group)

    for dir_path, dir_names, files in walk(path):
        for dir_name in dir_names:
            chown(join(dir_path, dir_name), user, group)

        for file in files:
            chown(join(dir_path, file), user, group)
