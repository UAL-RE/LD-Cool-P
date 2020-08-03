from ldcoolp.curation import df_to_dict_single


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

    curation_id : int
      Curation ID number associated with article_id

    curation_dict : dictionary
      dictionary containing detailed curation information

    name_dict : dictionary
      Dictionary containing all possible permutation of depositor name and
      list of authors

    folderName: str
      Preferred folder name for data curation process given article information

    Methods
    -------
    get_curation_id()
       Retrieve curation ID associated with article_id from Figshare API

    get_curation_dict()
       Retrieve curation dictionary containing curation details

    get_name_dict()
      Retrieve dictionary of depositor name information

    get_folder_name()
      Retrieve string containing preferred curation folder name for deposit
    """

    def __init__(self, article_id, fs_admin, verbose=True):
        self.article_id = article_id
        self.fs_admin = fs_admin
        self.verbose = verbose

        # Retrieves specific information for article (includes authors)
        self.curation_id   = self.get_curation_id()
        self.curation_dict = self.get_curation_dict()

        self.name_dict  = self.get_name_dict()
        self.folderName = self.get_folder_name()

    def get_curation_id(self):
        # This retrieves basic curation information for article
        cur_df = self.fs_admin.get_curation_list(article_id=self.article_id)
        cur_loc_dict = df_to_dict_single(cur_df)

        return cur_loc_dict['id']

    def get_curation_dict(self):
        # This retrieves specific information for article (includes authors)
        return self.fs_admin.get_curation_details(self.curation_id)

    def get_name_dict(self):
        if self.verbose:
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

        authors = [d['full_name'] for d in self.curation_dict['item']['authors']]
        name_dict['authors'] = authors

        if fullName in authors or simplify_fullName in authors:
            name_dict['self_deposit'] = True
        else:
            name_dict['self_deposit'] = False

        # Add additional information about deposit, such as article and
        # curation IDs, email, and title
        name_dict['article_id'] = self.article_id
        name_dict['curation_id'] = self.curation_id
        name_dict['depositor_email'] = temp_dict['email']
        name_dict['title'] = self.curation_dict['item']['title']

        return name_dict

    def get_folder_name(self):
        # Check to see if the depositor is in the list of authors

        if self.name_dict['self_deposit']:
            if self.verbose:
                print("  Depositor == author")
            folderName = self.name_dict['simplify_fullName']
        else:
            if self.verbose:
                print("  Depositor != author")
            folderName = '{} - {}'.format(self.name_dict['simplify_fullName'],
                                          self.name_dict['authors'][0])
        if self.verbose:
            print("depository_name : {}".format(folderName))
        return folderName
