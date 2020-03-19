import configparser

from figshare.figshare import Figshare

# Read in default configuration file
config = configparser.ConfigParser()
config.read('config/default.ini')

api_token = config.get('global', 'api_token')

if api_token is None or api_token == "***override***":
    print("ERROR: api_token not available from config file")
    api_token = input("Provide token through prompt : ")

fs = Figshare(token=api_token, private=True)


def curation_retrieve(article_id):

    # Retrieve article information
    article_details = fs.get_article_details(article_id)
