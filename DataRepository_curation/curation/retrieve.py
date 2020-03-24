import configparser

from figshare.figshare import Figshare  # , issue_request

# Read in default configuration file
config = configparser.ConfigParser()
config.read('config/default.ini')

api_token = config.get('global', 'api_token')

fs = Figshare(token=api_token, private=True)


def curation_retrieve(article_id):

    # Retrieve article information
    article_details = fs.get_article_details(article_id)
