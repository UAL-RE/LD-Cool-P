import requests
from requests.exceptions import HTTPError

from ...logger import log_stdout


def tiny_url(url, alias=None, log=None):
    """
    Purpose:
      Generate a TinyURL

    :param url: HTTP URL
    :param alias: Alias if desired
    :param log: LogClass or logger object

    :return: response_data: str containing the shortened TinyURL
    """
    if log is None:
        log = log_stdout()

    endpoint = "http://tinyurl.com/api-create.php"
    params = {'url': url}
    if alias is not None:
        params['alias'] = alias

    response = requests.get(endpoint, params=params)

    try:
        response.raise_for_status()
        response_data = response.text
    except HTTPError as error:
        log.warning(f"Caught an HTTPError: {error}")
        log.warning('Body:\n', response.text)
        raise

    return response_data
