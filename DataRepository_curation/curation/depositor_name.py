from DataRepository_curation.curation import df_to_dict_single


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

    name_dict : dictionary
      Dictionary containing all possible permutation of depositor name

    folderName: str
      Preferred folder name for data curation process given article information

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

        self.name_dict  = self.get()
        self.folderName = self.folder_name()

    def get(self):
        print("Retrieving depositor_name for {} ... ".format(self.article_id))

        account_id = self.curation_dict['account_id']
        temp_dict = df_to_dict_single(self.acct_df.loc[self.acct_df['id'] == account_id])

        surName            = temp_dict['last_name']   # full last name
        firstName          = temp_dict['first_name']  # full first name
        simplify_firstName = firstName.split(' ')[0]
        simplify_surName   = surName.split(' ')[0]
        fullName           = "{} {}".format(firstName, surName)
        simplify_fullName  = "{} {}".format(simplify_firstName, simplify_surName)

        name_dict = dict()
        name_dict['surName']   = surName
        name_dict['firstName'] = firstName
        name_dict['simplify_firstName'] = simplify_firstName
        name_dict['simplify_surName']   = simplify_surName
        name_dict['fullName']           = fullName
        name_dict['simplify_fullName']  = simplify_fullName

        return name_dict

    def folder_name(self):
        # Check to see if the depositor is in the list of authors
        authors = [d['full_name'] for d in self.curation_dict['item']['authors']]
        if self.name_dict['fullName'] in authors or \
                self.name_dict['simplify_fullName'] in authors:
            print("  Depositor == author")
            folderName = self.name_dict['simplify_fullName']
        else:
            print("  Depositor != author")
            folderName = '{} - {}'.format(self.name_dict['simplify_fullName'], authors[0])
        print("depository_name : {}".format(folderName))
        return folderName
