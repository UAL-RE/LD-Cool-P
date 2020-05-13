from . import df_to_dict_single


class DepositorName:
    """
    Purpose:
      Retrieve depositor information for a deposit

    Attributes
    ----------
    article_id : int
      Figshare article ID

    fs_admin :
      Figshare Admin object

    cur_df : pandas DataFrame
      pandas DataFrame containing full list of curation items

    acct_df : pandas DataFrame
      pandas DataFrame containing Figshare Institution accounts

    cur_loc_dict : dictionary
      dictionary containing general curation information

    curation_dict : dictionary
      dictionary containing detailed curation information

    Methods
    -------
    get()
      Retrieve dictionary of depositor name information

    depositor_folder_name()
      Retrieve string containing preferred curation folder name for deposit
    """

    def __init__(self, article_id, fs_admin):
        self.article_id = article_id
        self.cur_df = fs_admin.get_curation_list()
        self.acct_df = fs_admin.get_account_list()

        self.cur_loc_dict = df_to_dict_single(self.cur_df.loc[self.cur_df['article_id'] == self.article_id])
        self.curation_dict = fs_admin.get_curation_details(self.cur_loc_dict['id'])

        self.depositor_dict = self.get()
        self.depositor_folderName = self.depositor_folder_name()

    def get(self):
        print("Retrieving depositor_name for {} ... ".format(self.article_id))

        account_id = self.curation_dict['account_id']
        temp_dict = df_to_dict_single(self.acct_df.loc[self.acct_df['id'] == account_id])

        depositor_surName       = temp_dict['last_name']   # full last name
        depositor_firstName     = temp_dict['first_name']  # full first name
        depositor_simplifyFirst = depositor_firstName.split(' ')[0]
        depositor_simplifySur   = depositor_surName.split(' ')[0]
        depositor_fullName      = "{} {}".format(depositor_firstName,
                                                 depositor_surName)
        depositor_displayName   = "{} {}".format(depositor_simplifyFirst,
                                                 depositor_simplifySur)

        depositor_dict = dict()
        depositor_dict['depositor_surName']       = depositor_surName
        depositor_dict['depositor_firstName']     = depositor_firstName
        depositor_dict['depositor_simplifyFirst'] = depositor_simplifyFirst
        depositor_dict['depositor_simplifySur']   = depositor_simplifySur
        depositor_dict['depositor_fullName']      = depositor_fullName
        depositor_dict['depositor_displayName']   = depositor_displayName

        return depositor_dict

    def depositor_folder_name(self):
        # Check to see if the depositor is in the list of authors
        authors = [d['full_name'] for d in self.curation_dict['item']['authors']]
        if self.depositor_dict['depositor_fullName'] in authors or \
                self.depositor_dict['depositor_displayName'] in authors:
            print("  Depositor == author")
            depositor_folderName = self.depositor_dict['depositor_displayName']
        else:
            print("  Depositor != author")
            depositor_folderName = '{} - {}'.format(self.depositor_dict['depositor_displayName'],
                                                    authors[0])
        print("depository_name : {}".format(depositor_folderName))
        return depositor_folderName
