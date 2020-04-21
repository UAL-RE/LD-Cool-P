from os.path import exists, join
from os import walk


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
                if ignore:
                    if file_fullname != ignore:
                        print("File exists : {}".format(file_fullname))


def check(data_path):
    """
    Purpose:
      Check that a README file exists

    :param data_path: path to data folder
    :return: Will raise error
    """

    README_file_default = join(data_path, 'README.txt')
    if exists(README_file_default):
        print("Default README.txt file exists!!!")

        print("Checking for additional README files")
        walkthrough(data_path, ignore=README_file_default)
    else:
        print("Default README.txt file DOES NOT exist!!!")
        print("Searching other possible locations...")

        walkthrough(data_path)
