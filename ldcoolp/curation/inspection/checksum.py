import hashlib
from logging import Logger

from redata.commons.logger import log_stdout


def check_md5(filename: str, figshare_checksum: str,
              log: Logger = log_stdout()) -> bool:
    """
    Perform checksum after file retrieval against Figshare's computation

    :param filename: Full path of file on server
    :param figshare_checksum: MD5 checksum string from supplied_md5 metadata
    :param log: logger.LogClass object. Default is stdout via python logging

    :return: ``True`` if passed, ``False`` if not a match
    """

    log.info("Performing MD5 checksum ...")

    checksum_pass = False

    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        # Handle large files by chunking
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    checksum_compute = hash_md5.hexdigest()
    if checksum_compute == figshare_checksum:
        checksum_pass = True
        log.info("MD5 Checksum passed!!!")
    else:
        log.warning("Checksum failed!!!")
    log.info(f"MD5 Result:  {checksum_compute}")
    log.info(f"Expectation: {figshare_checksum}")

    return checksum_pass
