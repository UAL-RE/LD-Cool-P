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

root_directory = join(root_directory, underreview_folder)

readme_template = config.get('curation', 'readme_template')


class ReadmeClass:

    def __init__(self, dn):
        self.folderName = dn.folderName
        self.article_id = dn.article_id
        self.article_dict = dn.curation_dict

        self.data_path = join(root_directory, self.folderName,
                              folder_copy_data)
        self.readme_file_path = join(self.data_path, 'README.txt')

        self.readme_template = self.import_template()

        self.readme_dict = self.retrieve_article_metadata()

    def import_template(self):
        file_loader = FileSystemLoader(dirname(__file__))
        env = Environment(loader=file_loader)

        template = env.get_template(readme_template)
        return template

    def retrieve_article_metadata(self):
        """
        Purpose:
          Retrieve metadata from figshare API to strip out information to
          populate in README.txt file for basic content

        :return readme_dict: dict containing essential metadata for README.txt
        """

        readme_dict = dict()

        # Retrieve title of deposit
        readme_dict['title'] = self.article_dict['item']['title']

        # Retrieve preferred citation. Default: ReDATA in DataCite format
        # This forces a period after the year and ensures multiple rows
        # with the last two row merged for simplicity
        single_str_citation = self.article_dict['item']['citation']
        str_list = [str_row + '.' for str_row in
                    single_str_citation.replace('):', ').').split('. ')]
        citation_list = [content for content in str_list[0:-2]]
        citation_list.append(f"{str_list[-2]} {str_list[-1]}")
        readme_dict['preferred_citation'] = citation_list

        # If DOI available, retrieve:
        if 'doi' in self.article_dict['item']:
            readme_dict['doi'] = self.article_dict['item']['doi']
        else:
            readme_dict['doi'] = "10.25422/azu.data.[DOI_NUMBER]"

        # Retrieve license
        readme_dict['license'] = self.article_dict['item']['license']['name']

        # Retrieve author
        readme_dict['first_author'] = \
            self.article_dict['item']['authors'][0]['full_name']

        # Retrieve description (single string)
        readme_dict['description'] = self.article_dict['item']['description']

        # Retrieve references as list
        readme_dict['references'] = self.article_dict['item']['references']

        return readme_dict

    def construct(self):
        """
        Purpose:
          Create README.txt file with jinja2 README template and populate with
          metadata information

        :return:
        """

        # Write file
        f = open(self.readme_file_path, 'w')

        content_list = self.readme_template.render(readme_dict=self.readme_dict)
        f.writelines(content_list)
        f.close()

    def retrieve(self):
        """
        Purpose:
          Retrieve template of README.txt file if such file is not present

        :return: Download files and place it within the [folder_data] path
        """

        if not exists(self.readme_file_path):
            print("Constructing README template...")
            self.construct()
            permissions.curation(self.readme_file_path)
        else:
            print("Default README file found! Not overwriting with template!")

    def walkthrough(self, data_path, ignore=''):
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

    def check_exists(self):
        """
        Purpose:
          Check that a README file exists

        :return: Will raise error
        """

        if exists(self.readme_file_path):
            print("Default README.txt file exists!!!")

            print("Checking for additional README files")
            self.walkthrough(self.data_path, ignore=self.readme_file_path)
        else:
            print("Default README.txt file DOES NOT exist!!!")
            print("Searching other possible locations...")

            self.walkthrough(self.data_path)
