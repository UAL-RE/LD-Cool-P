from os.path import exists, join
from os import walk


def readme_walkthrough(data_path):
    """
    Purpose:
      Perform walkthrough to find other README files

    :param data_path:
    :return:
    """
    for dir_path, dir_names, files in walk(data_path):
        for file in files:
            if 'README' in file.upper():
                print("File exists : {}".format(join(dir_path, file)))


def readme_check(data_path):
    """
    Purpose:
      Check that a README file exists

    :param data_path: path to data folder
    :return: Will raise error
    """

    README_file_default = join(data_path, 'README.txt')
    if exists(README_file_default):
        print("Default README.txt file exists!!!")
    else:
        print("Default README.txt file DOES NOT exist!!!")
        print("Searching other possible locations")

        readme_walkthrough(data_path)
