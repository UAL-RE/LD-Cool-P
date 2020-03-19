import configparser

from figshare.figshare import Figshare

config = configparser.ConfigParser()
config.read('config/default.ini')

api_token = config.get('global', 'api_token')

fs = Figshare(token=api_token, private=True)

def curation_retrieve(article_id):

