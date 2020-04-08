from os.path import join, isdir
from os import chown, walk


def curation(path, user):
    """
    Purpose:
      Change user and group ownership of all folders and files
      under the parent location of [path]

    :param path: Parent location path
    :param user: The user name or UID (this will probably need to change)
    """

    group = 0  # Placeholder

    if isdir(path):
        chown(path, user, group)

    for dir_path, dir_names, files in walk(path):
        for dir_name in dir_names:
            chown(join(dir_path, dir_name), user, group)

        for file in files:
            chown(join(dir_path, file), user, group)
