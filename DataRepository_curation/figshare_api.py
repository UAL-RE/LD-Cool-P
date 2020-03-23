import configparser

import requests
import json
from requests.exceptions import HTTPError

from figshare.figshare import Figshare  # , issue_request

import pandas as pd

# Read in default configuration file
config = configparser.ConfigParser()
config.read('config/default.ini')

api_token = config.get('global', 'api_token')

if api_token is None or api_token == "***override***":
    print("ERROR: api_token not available from config file")
    api_token = input("Provide token through prompt : ")

fs = Figshare(token=api_token, private=True)


def issue_request(method, url, headers, params=None, data=None, binary=False):
    """Wrapper for HTTP request

    Parameters
    ----------
    method : str
        HTTP method. One of GET, PUT, POST or DELETE

    url : str
        URL for the request

    headers: dict
        HTTP header information

    params: dict
        Additional information for URL GET request

    data: dict
        Figshare article data

    binary: bool
        Whether data is binary or not

    Returns
    -------
    response_data: dict
        JSON response for the request returned as python dict
    """
    if data is not None and not binary:
        data = json.dumps(data)

    response = requests.request(method, url, params=params,
                                headers=headers, data=data)

    try:
        response.raise_for_status()
        try:
            response_data = json.loads(response.text)
        except ValueError:
            response_data = response.content
    except HTTPError as error:
        print('Caught an HTTPError: {}'.format(error))
        print('Body:\n', response.text)
        raise

    return response_data


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
        Return pandas DataFrame private account institution groups

    institute_accounts()
        Return pandas DataFrame private account institution accounts

    account_group_roles()
        Return dict containing group roles for a given account

    account_details()
        Return dict containing group roles for all accounts
    """
    def __init__(self, token=None, private=False):
        self.baseurl = "https://api.figshare.com/v2/account/institution/"
        self.token = token
        self.private = private

        self.headers = {'Content-Type': 'application/json'}
        if token:
            self.headers['Authorization'] = 'token {0}'.format(token)

    def endpoint(self, link):
        """Concatenate the endpoint to the baseurl"""
        return self.baseurl + link

    def institute_articles(self):
        url = self.endpoint("articles")
        articles = issue_request('GET', url, self.headers)
        return articles

    def institute_groups(self):
        url = self.endpoint("groups")
        groups = issue_request('GET', url, self.headers)

        groups_df = pd.DataFrame(groups)
        return groups_df

    def institute_accounts(self):
        url = self.endpoint("accounts")

        # Figshare API is limited to a maximum of 1000 per page
        params = {'page': 1, 'page_size': 1000}
        accounts = issue_request('GET', url, self.headers, params=params)

        accounts_df = pd.DataFrame(accounts)
        accounts_df = accounts_df.drop(columns='institution_id')
        return accounts_df

    def account_group_roles(self, account_id):
        url = self.endpoint("roles/{}".format(account_id))

        roles = issue_request('GET', url, self.headers)
        return roles

    def account_details(self):
        # Retrieve accounts
        accounts_df = self.institute_accounts()

        # Determine group roles for each account
        for account_id in accounts_df['id']:
            roles = self.account_group_roles(account_id)
            print(roles)


def curation_retrieve(article_id):

    # Retrieve article information
    article_details = fs.get_article_details(article_id)
