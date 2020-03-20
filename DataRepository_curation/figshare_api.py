import configparser

from figshare.figshare import Figshare, issue_request

# Read in default configuration file
config = configparser.ConfigParser()
config.read('config/default.ini')

api_token = config.get('global', 'api_token')

if api_token is None or api_token == "***override***":
    print("ERROR: api_token not available from config file")
    api_token = input("Provide token through prompt : ")

fs = Figshare(token=api_token, private=True)


class FigshareAdmin:
    """ A Python interface to Figshare administration

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

    """
    def __init__(self, token=None, private=False):
        self.baseurl = "https://api.figshare.com/v2"
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

        url = self.endpoint("/account/institution/articles")
        articles = issue_request('GET', url, headers)
        return articles


def curation_retrieve(article_id):

    # Retrieve article information
    article_details = fs.get_article_details(article_id)
