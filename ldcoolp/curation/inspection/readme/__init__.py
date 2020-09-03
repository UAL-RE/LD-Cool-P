from os.path import exists, join, dirname, basename
from os import walk
import shutil
from glob import glob

# Template engine
from jinja2 import Environment, FileSystemLoader
from html2text import html2text

# Logging
from ldcoolp.logger import log_stdout

from ....admin import permissions

# Read in default configuration settings
from ....config import folder_copy_data, folder_data, root_directory_main
from ....config import todo_folder, readme_template

root_directory = join(root_directory_main, todo_folder)


class ReadmeClass:
    """
    Purpose:
      A ReadmeClass object for retrieval and population of README.txt
      files.  It uses existing metadata information from Figshare to
      populate common information that are provided

    Attributes
    ----------
    dn : DepositorName object
      Contains information about the depositor and author(s)

    folderName : str
      Folder name identifying depositor and corresponding author

    article_id : int
      Figshare article ID

    article_dict : dict
      dictionary containing curation details

    data_path : str
      Path DATA folder (this is the working copy and not the ORIGINAL_DATA)

    readme_file_path : str
      Full filename for exported README.txt

    readme_template: jinja2.environment.Template

    readme_dict : dict
      Dictionary containing metadata information to provide to jinja template

    Methods
    -------
    get_readme_files()
      Return list of README files in the ORIGINAL_DATA path

    check_for_readme()
      Check if a README file is provided and provide list of README files

    save_template()
      Save either default or user-provided templates in DATA path

    import_template()
     Returns a jinja2 template by importing markdown README file (README_template.md)

    retrieve article_metadata()
      Returns a dictionary containing metadata for jinja2 template

    construct()
      Create README.txt file with jinja2 README template and populate with metadata information

    main()
      Construct README.txt by calling retrieve
    """

    def __init__(self, dn, log=None):
        self.dn = dn
        self.folderName = self.dn.folderName
        self.article_id = self.dn.article_id
        self.article_dict = self.dn.curation_dict

        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
            self.log = log

        # Paths
        self.folder_path = join(root_directory, self.folderName)
        self.data_path = join(self.folder_path, folder_copy_data)      # DATA
        self.original_data_path = join(self.folder_path, folder_data)  # ORIGINAL_DATA

        # This is the full path of the final README.txt file for creation
        self.readme_file_path = join(self.data_path, 'README.txt')

        # Retrieve Figshare metadata for jinja template engine
        self.readme_dict = self.retrieve_article_metadata()

        # Retrieve list of README files provided by user
        self.README_files = self.get_readme_files()

        try:
            # Define template_source
            self.template_source = self.check_for_readme()

            # Save copy of template in DATA as README_template.md
            self.save_template()

            # Import README template as jinja2 template
            self.readme_template = self.import_template()
        except SystemError:
            self.template_source = 'unknown'
            self.log.warn("More than one README files found!")

    def get_readme_files(self):
        """Return list of README files in the ORIGINAL_DATA path"""
        README_files = glob(join(self.original_data_path, 'README*.txt'))
        README_files += glob(join(self.original_data_path, 'README*.md'))

        return README_files

    def check_for_readme(self):
        """Check if a README file is provided and provide list of README files"""

        if len(self.README_files) == 0:
            self.log.info("No README files found.")
            self.log.info(f"Note: default {readme_template} will be used")
            template_source = 'default'
        else:
            if len(self.README_files) == 1:
                self.log.info("Only one README file found!")

                self.log.info("PROMPT: Type 'Yes'/'yes' if you wish to use as template.")
                src_input = input("PROMPT: Anything else will use 'default' : ")
                self.log.info(f"RESPONSE: {src_input}")

                if src_input.lower() == 'yes':
                    template_source = 'user'
                else:
                    template_source = 'default'
            else:
                self.log.warn("More than one README file found!")
                self.log.warn("Manual intervention needed ...")
                raise SystemError
                # print(f"Select and save a README file in {copy_path} as {readme_template}")

        return template_source

    def save_template(self):
        """Save either default or user-provided templates in DATA path"""

        dest_file = join(self.data_path, readme_template)

        if not exists(dest_file):
            self.log.info(f"Saving {self.template_source} template in DATA ...")

            if self.template_source == 'default':
                src_file = join(dirname(__file__), readme_template)
            else:
                src_file = self.README_files[0]

            shutil.copy(src_file, dest_file)
        else:
            self.log.info(f"{readme_template} exists. Not overwriting template!")

    def import_template(self):
        """Returns a jinja2 template by importing README markdown template (README_template.md)"""

        file_loader = FileSystemLoader(self.data_path)
        env = Environment(loader=file_loader)

        jinja_template = env.get_template(readme_template)
        return jinja_template

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

        # Retrieve DOI info. Reserve if it does not exist
        if not self.article_dict['item']['doi']:
            # Reserve DOI
            doi_string = self.dn.fs_admin.reserve_doi(self.article_id)

            readme_dict['doi'] = doi_string
        else:
            readme_dict['doi'] = f"10.25422/azu.data.{self.article_id} [DOI NOT MINTED!]"

        readme_dict['lastname'] = self.dn.name_dict['surName']
        readme_dict['firstname'] = self.dn.name_dict['firstName']
        readme_dict['email'] = self.dn.name_dict['depositor_email']

        # Retrieve license
        readme_dict['license'] = self.article_dict['item']['license']['name']

        # Retrieve author
        readme_dict['first_author'] = \
            self.article_dict['item']['authors'][0]['full_name']

        # Retrieve description (single string)
        readme_dict['description'] = html2text(self.article_dict['item']['description'])

        # Retrieve references as list
        readme_dict['references'] = self.article_dict['item']['references']

        return readme_dict

    def construct(self):
        """Create README.txt file with jinja2 README template and populate with metadata information"""

        if not exists(self.readme_file_path):
            self.log.info(f"Constructing README.txt file based on {self.template_source} template ...")

            # Write file
            self.log.info(f"Writing file : {self.readme_file_path}")
            f = open(self.readme_file_path, 'w')

            content_list = self.readme_template.render(readme_dict=self.readme_dict)
            f.writelines(content_list)
            f.close()
        else:
            self.log.warn("Default README.txt file found! Not overwriting with template!")

        # Set permission for rwx
        permissions.curation(self.readme_file_path)

    def main(self):
        """Main function for README file construction"""

        if self.template_source != 'unknown':
            self.log.info("PROMPT: Do you wish to create a README file?")
            user_response = input("PROMPT: Type 'Yes'/'yes'. Anything else will exit : ")
            self.log.info(f"RESPONSE: {user_response}")
            if user_response.lower() == "yes":
                self.construct()
            else:
                self.log.warn("Exiting script")
                return
        else:
            self.log.warn(f"Multiple README files. Unable to save {readme_template} and README.txt")


def walkthrough(data_path, ignore='', log=None):
    """
    Purpose:
      Perform walkthrough to find other README files

    :param data_path: path to DATA folder
    :param ignore: full path of default README.txt to ignore
    :param log: logger.LogClass object. Default is stdout via python logging
    :return:
    """

    if isinstance(log, type(None)):
        log = log_stdout()
    else:
        log = log

    for dir_path, dir_names, files in walk(data_path):
        for file in files:
            if 'README' in file.upper():  # case insensitive
                file_fullname = join(dir_path, file)
                if file_fullname != ignore:
                    log.info(f"File exists : {file_fullname}")
