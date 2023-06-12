import requests
from requests.exceptions import HTTPError

from urllib.parse import quote, urlencode
from ..api.qualtrics import url_safe

from redata.commons.logger import log_stdout


def tiny_url(url: str, alias=None, log=None) -> str:
    """
    Purpose:
      Generate a TinyURL

    :param url: str. HTTP URL
    :param alias: str. Alias if desired
    :param log: LogClass or logger object

    :return: response_data: str containing the shortened TinyURL
    """
    if log is None:
        log = log_stdout()

    endpoint = "http://tinyurl.com/api-create.php"
    encoded_url = urlencode({'url': url}, safe=url_safe, quote_via=quote)
    log.debug(f"encoded_url: {encoded_url}")
    get_url = f"{endpoint}?{encoded_url}"
    log.debug(f"get_url : {get_url}")

    params = dict()
    if alias is not None:
        params = {'alias': alias}

    expected_url = f"https://tinyurl.com/{alias}"

    expected_response = requests.get(expected_url)
    if expected_response.status_code == 200:
        log.info(f"TinyURL link already exists!")

        expected_request_url = f"{url}&alias={alias}"
        if expected_response.url != expected_request_url:
            log.warning(f"Input URL changed!")
            log.debug(f"Previous URL: {expected_response.url}")
            log.debug(f"New URL: {expected_request_url}")
            log.warning(f"Creating new TinyURL")
            response = requests.get(get_url)
            response_data = response.text
        else:
            response_data = expected_url
    else:
        log.info(f"TinyURL link does not exist. Creating!")
        # GET still works if the TinyURL alias exists, but points to the same URL
        if len(alias) > 30:
            response = requests.get(get_url)   # TinyURL alias must be 30 chars or less.
        else:
            response = requests.get(get_url, params=params)

        try:
            response.raise_for_status()
            response_data = response.text
        except HTTPError as error:
            log.warning(f"Caught an HTTPError: {error}")
            return "error"

    return response_data
