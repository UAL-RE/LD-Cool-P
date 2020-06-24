from os.path import exists, join, dirname
from os import walk

# Template engine
from jinja2 import Environment, FileSystemLoader

from ....admin import permissions
from . import populate

import configparser

# Read in default configuration file
from ldcoolp import config_file
config = configparser.ConfigParser()
config.read(config_file)

folder_copy_data = config.get('curation', 'folder_copy_data')
folder_data = config.get('curation', 'folder_data')

source = config.get('curation', 'source')
root_directory = config.get('curation', '{}_path'.format(source))

underreview_folder = config.get('curation', 'folder_underreview')

staging_directory = join(root_directory, underreview_folder)

readme_template = config.get('curation', 'readme_template')


def construct(README_file_default, readme_dict):
    """
    Purpose:
      Create README.txt file with jinja2 README template and populate with
      metadata information

    :return:
    """

    file_loader = FileSystemLoader(dirname(__file__))

    env = Environment(loader=file_loader)

    template = env.get_template(readme_template)

    # Write file
    f = open(README_file_default, 'w')

    content_list = template.render(readme_dict=readme_dict)
    f.writelines(content_list)
    f.close()


def default_readme_path(depositor_name):
    """
    Purpose:
      Provide full path for default README.txt file and data_path

    :param depositor_name: Exact name of the data curation folder with spaces

    :return README_file_default: str containing full path
    :return data_path: full path to DATA folder
    """

    data_path = join(staging_directory, depositor_name, folder_copy_data)

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


def retrieve(depositor_name, article_id):
    """
    Purpose:
      Retrieve template of README.txt file if such file is not present

    :param depositor_name: Exact name of the data curation folder with spaces
    :return: Download files and place it within the [folder_data] path
    """

    README_file_default, _ = default_readme_path(depositor_name)

    if not exists(README_file_default):
        print("Constructing README template...")
        readme_dict = populate.retrieve_article_metadata(article_id)
        construct(README_file_default, readme_dict)
        permissions.curation(README_file_default)
    else:
        print("Default README file found! Not overwriting with template!")

