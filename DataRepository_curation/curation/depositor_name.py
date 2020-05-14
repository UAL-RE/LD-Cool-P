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

    folder_name()
      Retrieve string containing preferred curation folder name for deposit
    """

    def __init__(self, article_id, fs_admin):
        self.article_id = article_id
        self.fs_admin = fs_admin

        # Retrieves specific information for article (includes authors)
        self.curation_id   = self.get_curation_id()
        self.curation_dict = self.curation_dict()

        self.name_dict  = self.get()
        self.folderName = self.folder_name()

    def get_curation_id(self):
        # This retrieves basic curation information for article
        cur_df = self.fs_admin.get_curation_list()
        cur_loc_dict = df_to_dict_single(cur_df.loc[cur_df['article_id'] == self.article_id])

        return cur_loc_dict['id']

    def curation_dict(self):
        # This retrieves specific information for article (includes authors)
        return self.fs_admin.get_curation_details(self.curation_id)

    def get(self):
        print("Retrieving depositor_name for {} ... ".format(self.article_id))

        account_id = self.curation_dict['account_id']
        acct_df = self.fs_admin.get_account_list()

        temp_dict = df_to_dict_single(acct_df.loc[acct_df['id'] == account_id])

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
