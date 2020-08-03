from figshare.figshare import Figshare  # , issue_request

# Read in default configuration settings
from ....config import api_token

if api_token is None or api_token == "***override***":
    print("ERROR: api_token not available from config file")
    api_token = input("Provide token through prompt : ")

fs = Figshare(token=api_token, private=True)


def retrieve_article_metadata(article_id):
    """
    Purpose:
      Retrieve metadata from figshare API to strip out information to
      populate in README.txt file for basic content

    :param article_id: int providing the figshare article ID
    :return readme_dict: dict containing essential metadata for README.txt
    """

    # Retrieve article details
    article_dict = fs.get_article_details(article_id)

    readme_dict = dict()

    # Retrieve title of deposit
    readme_dict['title'] = article_dict['title']

    # Retrieve preferred citation. Default: ReDATA in DataCite format
    # This forces a period after the year and ensures multiple rows
    # with the last two row merged for simplicity
    single_str_citation = article_dict['citation']
    str_list = [str_row+'.' for str_row in
                single_str_citation.replace('):', ').').split('. ')]
    citation_list = [content for content in str_list[0:-2]]
    citation_list.append(f"{str_list[-2]} {str_list[-1]}")
    readme_dict['preferred_citation'] = citation_list

    # If DOI available, retrieve:
    if 'doi' in article_dict:
        readme_dict['doi'] = article_dict['doi']
    else:
        readme_dict['doi'] = "10.25422/azu.data.[DOI_NUMBER]"

    # Retrieve license
    readme_dict['license'] = article_dict['license']['name']

    # Retrieve author
    readme_dict['first_author'] = article_dict['authors'][0]['full_name']

    # Retrieve description (single string)
    readme_dict['description'] = article_dict['description']

    # Retrieve references as list
    readme_dict['references'] = article_dict['references']

    return readme_dict
