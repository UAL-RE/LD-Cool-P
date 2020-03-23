import configparser

from figshare.figshare import Figshare, issue_request

import pandas as pd

# Read in default configuration file
config = configparser.ConfigParser()
config.read('config/default.ini')

api_token = config.get('global', 'api_token')

if api_token is None or api_token == "***override***":
    print("ERROR: api_token not available from config file")
    api_token = input("Provide token through prompt : ")

fs = Figshare(token=api_token, private=True)


class FigshareAdmin:
    """
    Purpose:
      A Python interface to Figshare administration

    Attributes
    ----------
    baseurl : str
        Base URL of the Figshare v2 API

    token : str
        The Figshare OAuth2 authentication token

    private : bool
        Boolean to check whether connection is to a private or public article

    Methods
    -------
    endpoint(link)
        Concatenate the endpoint to the baseurl

    get_headers()
        Return the HTTP header string

    institute_articles()
        Return private institution articles

    institute_groups()
        Return private account institution groups

    institute_accounts()
        Return private account institution accounts
    """
    def __init__(self, token=None, private=False):
        self.baseurl = "https://api.figshare.com/v2/account/institution/"
        self.token = token
        self.private = private

    def endpoint(self, link):
        """Concatenate the endpoint to the baseurl"""
        return self.baseurl + link

    def get_headers(self, token=None):
        """ HTTP header information"""
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'token {0}'.format(token)

        return headers

    def institute_articles(self):
        headers = self.get_headers(token=self.token)

        url = self.endpoint("articles")
        articles = issue_request('GET', url, headers)
        return articles

    def institute_groups(self):
        headers = self.get_headers(token=self.token)

        url = self.endpoint("groups")
        groups = issue_request('GET', url, headers)
        return groups

    def institute_accounts(self):
        headers = self.get_headers(token=self.token)

        url = self.endpoint("accounts")
        accounts = issue_request('GET', url, headers)

        accounts_df = pd.DataFrame(accounts)
        accounts_df = accounts_df.drop(columns='institution_id')
        return accounts_df


def curation_retrieve(article_id):

    # Retrieve article information
    article_details = fs.get_article_details(article_id)
