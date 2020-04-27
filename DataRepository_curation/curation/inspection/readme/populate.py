from figshare.figshare import Figshare  # , issue_request

# Read in default configuration file
config = configparser.ConfigParser()
config.read('DataRepository_curation/config/default.ini')

api_token = config.get('global', 'api_token')

if api_token is None or api_token == "***override***":
    print("ERROR: api_token not available from config file")
    api_token = input("Provide token through prompt : ")

fs = Figshare(token=api_token, private=True)


def retrieve_article_metadata(article_id):

    # Retrieve article details
    article_dict = fs.get_article_details(article_id)

    # Retrieve title of deposit
    title = article_dict['title']

    # Retrieve preferred citation. Default: ReDATA in DataCite format
    preferred_citation = article_dict['citation']

    # If DOI available, retrieve:
    if 'doi' in article_dict:
        doi = article_dict['doi']

    # Retrieve license
    license = article_dict['license']['name']

    # Retrieve author
    first_author = article_dict['authors'][0]['full_name']
