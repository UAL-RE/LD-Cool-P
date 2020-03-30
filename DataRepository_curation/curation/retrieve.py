import configparser

from urllib.request import Request, urlopen

from figshare.figshare import Figshare  # , issue_request
from ..figshare_api import FigshareInstituteAdmin

# Read in default configuration file
config = configparser.ConfigParser()
config.read('config/default.ini')

api_token = config.get('global', 'api_token')

if api_token is None or api_token == "***override***":
    print("ERROR: api_token not available from config file")
    api_token = input("Provide token through prompt : ")

fs = Figshare(token=api_token, private=True)

# fs_admin = FigshareInstituteAdmin(token=api_token)


def private_file_retrieve(url, filename=None, token=None):

    req = Request(url)
    if token:
        req.add_header('Authorization', 'token {}'.format(token))

    response = urlopen(req)
    content = response.read()
    print(url)

    f = open(filename, 'wb')
    f.write(content)
    f.close()


def curation_retrieve(article_id):

    # Retrieve article information
    article_details = fs.get_article_details(article_id)

    file_list = fs.list_files(article_id)

    for file_dict in file_list:
        private_file_retrieve(file_dict['download_url'],
                              filename=file_dict['name'], token=api_token)
