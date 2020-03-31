from figshare.figshare import issue_request

import pandas as pd


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
      Return pandas DataFrame of institution articles
      See: https://docs.figshare.com/#private_institution_articles

    get_groups()
      Return pandas DataFrame of account institution groups
      See: https://docs.figshare.com/#private_institution_groups_list

    get_account_list()
      Return pandas DataFrame of account institution accounts
      See: https://docs.figshare.com/#private_institution_accounts_list

    get_account_group_roles(account_id)
      Return dict containing group roles for a given account
      See: https://docs.figshare.com/#private_institution_account_group_roles

    get_account_details()
      Return dict containing group roles for all accounts
    """

    def __init__(self, token=None):
        self.baseurl = "https://api.figshare.com/v2/account/institution/"
        self.token = token

        self.headers = {'Content-Type': 'application/json'}
        if token:
            self.headers['Authorization'] = 'token {0}'.format(token)

    def endpoint(self, link):
        """Concatenate the endpoint to the baseurl"""
        return self.baseurl + link

    def get_articles(self):
        """Retrieve information about articles within institutional instance"""
        url = self.endpoint("articles")

        # Figshare API is limited to a maximum of 1000 per page
        params = {'page': 1, 'page_size': 1000}
        articles = issue_request('GET', url, self.headers, params=params)

        articles_df = pd.DataFrame(articles)
        return articles_df

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

        admin_flag = [''] * n_accounts
        reviewer_flag = [''] * n_accounts
        group_assoc = ['N/A'] * n_accounts

        # Determine group roles for each account
        for n, account_id in zip(range(n_accounts), accounts_df['id']):
            roles = self.get_account_group_roles(account_id)

            for key in roles.keys():
                for t_dict in roles[key]:
                    if t_dict['id'] == 2:
                        admin_flag[n] = 'X'
                    if t_dict['id'] == 49:
                        reviewer_flag[n] = 'X'
                    if t_dict['id'] == 11:
                        group_assoc[n] = key

        accounts_df['Admin'] = admin_flag
        accounts_df['Reviewer'] = reviewer_flag

        for group_id, group_name in zip(groups_df['id'], groups_df['name']):
            print(group_id, group_name)
            group_assoc = [sub.replace(str(group_id), group_name) for
                           sub in group_assoc]

        accounts_df['Group'] = group_assoc

        return accounts_df
