import configparser

from figshare.figshare import Figshare  # , issue_request

# Read in default configuration file
from ldcoolp import config_file
config = configparser.ConfigParser()
config.read(config_file)

api_token = config.get('global', 'api_token')

if api_token is None or api_token == "***override***":
    print("ERROR: api_token not available from config file")
    api_token = input("Provide token through prompt : ")

fs = Figshare(token=api_token, private=True)


def retrieve_article_metadata(article_id):
    """
    Purpose:
      Retrieve metadata from figshare API to strip out information to
      populate in README.txt file for basic content

    :param article_id: int providing the figshare article ID
    :return readme_dict: dict containing essential metadata for README.txt
    """

    # Retrieve article details
    article_dict = fs.get_article_details(article_id)

    readme_dict = dict()

    # Retrieve title of deposit
    readme_dict['title'] = article_dict['title']

    # Retrieve preferred citation. Default: ReDATA in DataCite format
    readme_dict['preferred_citation'] = article_dict['citation']

    # If DOI available, retrieve:
    if 'doi' in article_dict:
        readme_dict['doi'] = article_dict['doi']

    # Retrieve license
    readme_dict['license'] = article_dict['license']['name']

    # Retrieve author
    readme_dict['first_author'] = article_dict['authors'][0]['full_name']

    return readme_dict
