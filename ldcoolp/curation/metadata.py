from typing import Union

import os
import json

import pandas as pd

from ..logger import log_stdout


def save_metadata(json_response: Union[list, dict],
                  out_file_prefix: str,
                  root_directory: str = '',
                  metadata_directory: str = '',
                  save_csv: bool = False,
                  log=None):

    """
    Write metadata contents to JSON and CSV file

    :param json_response: Content in list or dict
    :param out_file_prefix: Filename prefix. Appends .json and .csv
    :param root_directory: Full path containing the working directory
    :param metadata_directory: Metadata path
    :param save_csv: Save a CSV file. Default: False
    :param log: LogClass or logging object. Default: log_stdout()
    """

    if log is None:
        log = log_stdout()

    log.debug("starting ...")
    log.info("")
    log.info("** SAVING CURATION METADATA **")

    if not root_directory:
        root_directory = os.getcwd()

    metadata_path = os.path.join(root_directory, metadata_directory)

    out_file_prefix = f"{metadata_path}/{out_file_prefix}"

    # Write JSON file
    json_out_file = f"{out_file_prefix}.json"
    if not os.path.exists(json_out_file):
        log.info(f"Writing: {json_out_file}")
        with open(json_out_file, 'w') as f:
            json.dump(json_response, f, indent=4)
    else:
        log.info(f"File exists: {out_file_prefix}")

    # Write CSV file
    if save_csv:
        csv_out_file = f"{out_file_prefix}.csv"
        df = pd.DataFrame.from_dict(json_response, orient='columns')
        log.info(f"Writing: {csv_out_file}")
        df.to_csv(csv_out_file, index=False)

    log.debug("finished.")
