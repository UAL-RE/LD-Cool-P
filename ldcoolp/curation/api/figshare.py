from figshare.figshare import issue_request

import pandas as pd
import numpy as np


class FigshareInstituteAdmin:
    """
    Purpose:
      A Python interface for administration of institutional Figshare accounts

    Attributes
    ----------
    baseurl : str
      Base URL of the Figshare v2 API

    token : str
      The Figshare OAuth2 authentication token

    headers : dict
      HTTP header information

    Methods
    -------
    endpoint(link)
      Concatenate the endpoint to the baseurl

    get_articles()
      Return pandas DataFrame of institutional articles
      See: https://docs.figshare.com/#private_institution_articles

    get_user_articles(account_id)
      Impersonate a user to retrieve articles associated with the user
      See: https://docs.figshare.com/#private_articles_list

    get_user_projects(account_id)
      Impersonate a user to retrieve projects associated with the user
      See: https://docs.figshare.com/#private_projects_list

    get_user_collections(account_id)
      Impersonate a user to retrieve collections associated with the user
      See: https://docs.figshare.com/#private_collections_list

    get_groups()
      Return pandas DataFrame of an institution's groups
      See: https://docs.figshare.com/#private_institution_groups_list

    get_account_list()
      Return pandas DataFrame of user accounts
      See: https://docs.figshare.com/#private_institution_accounts_list

    get_account_group_roles(account_id)
      Return dict containing group roles for a given account
      See: https://docs.figshare.com/#private_institution_account_group_roles

    get_account_details()
      Return pandas DataFrame that contains user information and their
      institutional and group roles

    get_curation_list()
      Return pandas DataFrame of datasets under curatorial review
      See: https://docs.figshare.com/#account_institution_curations

    get_curation_details(curation_id)
      Return dict containing curatorial details of a dataset

    get_curation_comments(curation_id)
      Return list containing curatorial comments of a dataset
      See: https://docs.figshare.com/#account_institution_curation_comments
    """

    def __init__(self, token=None):
        self.baseurl = "https://api.figshare.com/v2/account/"
        self.baseurl_institute = self.baseurl + "institution/"
        self.token = token

        self.headers = {'Content-Type': 'application/json'}
        if token:
            self.headers['Authorization'] = 'token {0}'.format(token)

    def endpoint(self, link, institute=True):
        """Concatenate the endpoint to the baseurl"""
        if institute:
            return self.baseurl_institute + link
        else:
            return self.baseurl + link

    def get_articles(self):
        """Retrieve information about articles within institutional instance"""
        url = self.endpoint("articles")

        # Figshare API is limited to a maximum of 1000 per page
        params = {'page': 1, 'page_size': 1000}
        articles = issue_request('GET', url, self.headers, params=params)

        articles_df = pd.DataFrame(articles)
        return articles_df

    def get_user_articles(self, account_id):
        url = self.endpoint("articles", institute=False)

        # Figshare API is limited to a maximum of 1000 per page
        params = {'page': 1, 'page_size': 1000, 'impersonate': account_id}
        user_articles = issue_request('GET', url, self.headers, params=params)

        user_articles_df = pd.DataFrame(user_articles)
        return user_articles_df

    def get_user_projects(self, account_id):
        url = self.endpoint("projects", institute=False)

        # Figshare API is limited to a maximum of 1000 per page
        params = {'page': 1, 'page_size': 1000, 'impersonate': account_id}
        user_projects = issue_request('GET', url, self.headers, params=params)

        user_projects_df = pd.DataFrame(user_projects)
        return user_projects_df

    def get_user_collections(self, account_id):
        url = self.endpoint("collections", institute=False)

        # Figshare API is limited to a maximum of 1000 per page
        params = {'page': 1, 'page_size': 1000, 'impersonate': account_id}
        user_collections = issue_request('GET', url, self.headers, params=params)

        user_collections_df = pd.DataFrame(user_collections)
        return user_collections_df

    def get_groups(self):
        """Retrieve information about groups within institutional instance"""
        url = self.endpoint("groups")
        groups = issue_request('GET', url, self.headers)

        groups_df = pd.DataFrame(groups)
        return groups_df

    def get_account_list(self):
        """Retrieve accounts within institutional instance"""
        url = self.endpoint("accounts")

        # Figshare API is limited to a maximum of 1000 per page
        params = {'page': 1, 'page_size': 1000}
        accounts = issue_request('GET', url, self.headers, params=params)

        accounts_df = pd.DataFrame(accounts)
        accounts_df = accounts_df.drop(columns='institution_id')
        return accounts_df

    def get_account_group_roles(self, account_id):
        """Retrieve group roles for a given account"""
        url = self.endpoint("roles/{}".format(account_id))

        roles = issue_request('GET', url, self.headers)
        return roles

    def get_account_details(self):
        # Retrieve accounts
        accounts_df = self.get_account_list()
        n_accounts = accounts_df.shape[0]

        # Retrieve groups
        groups_df = self.get_groups()

        num_articles = np.zeros(n_accounts, dtype=np.int)
        num_projects = np.zeros(n_accounts, dtype=np.int)
        num_collections = np.zeros(n_accounts, dtype=np.int)

        admin_flag = [''] * n_accounts
        reviewer_flag = [''] * n_accounts
        group_assoc = ['N/A'] * n_accounts

        # Determine group roles for each account
        for n, account_id in zip(range(n_accounts), accounts_df['id']):
            roles = self.get_account_group_roles(account_id)

            try:
                articles_df = self.get_user_articles(account_id)
                num_articles[n] = articles_df.shape[0]
            except Exception as e:
                print("Unable to retrieve articles for : {}".format(account_id))

            try:
                projects_df = self.get_user_projects(account_id)
                num_projects[n] = projects_df.shape[0]
            except Exception as e:

                print("Unable to retrieve projects for : {}".format(account_id))

            try:
                collections_df = self.get_user_collections(account_id)
                num_collections[n] = collections_df.shape[0]
            except Exception as e:
                print("Unable to retrieve collections for : {}".format(account_id))

            for key in roles.keys():
                for t_dict in roles[key]:
                    if t_dict['id'] == 2:
                        admin_flag[n] = 'X'
                    if t_dict['id'] == 49:
                        reviewer_flag[n] = 'X'
                    if t_dict['id'] == 11:
                        group_assoc[n] = key

        accounts_df['Articles'] = num_articles
        accounts_df['Projects'] = num_projects
        accounts_df['Collections'] = num_collections

        accounts_df['Admin'] = admin_flag
        accounts_df['Reviewer'] = reviewer_flag

        for group_id, group_name in zip(groups_df['id'], groups_df['name']):
            print(group_id, group_name)
            group_assoc = [sub.replace(str(group_id), group_name) for
                           sub in group_assoc]

        accounts_df['Group'] = group_assoc

        return accounts_df

    def get_curation_list(self):
        url = self.endpoint("reviews")

        params = {'page': 1, 'page_size': 1000}
        curation_list = issue_request('GET', url, self.headers, params=params)

        curation_df = pd.DataFrame(curation_list)
        return curation_df

    def get_curation_details(self, curation_id):
        url = self.endpoint("review/{}".format(curation_id))

        curation_details = issue_request('GET', url, self.headers)

        return curation_details

    def get_curation_comments(self, curation_id):
        url = self.endpoint("review/{}/comments".format(curation_id))

        curation_comments = issue_request('GET', url, self.headers)

        return curation_comments
