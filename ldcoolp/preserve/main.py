from pathlib import Path

from logging import Logger
from redata.commons.logger import log_stdout

# LD-Cool-P specific
from figshare.figshare import Figshare
from ..config import config_default_dict
from ..curation import metadata
from ..curation.inspection import checksum


class Preserve:
    """
    Primary class for the preparation of curated datasets for data
    preservation.

    This ``class`` includes a number of built-in features such as
    checking against the published metadata via MD5 checksum,
    saving a JSON file containing the published metadata, deleting
    hidden files, and changing curated folder to read-only

    Attributes
    ----------
    article_id: Figshare article ID
    version_no: Version number for article ID. Default: v1
    """

    def __init__(self, article_id: int, version_no: int = 1,
                 config_dict: dict = config_default_dict,
                 log: Logger = log_stdout()):

        self.log = log
        self.article_id = article_id
        self.version_no = version_no

        self.fs = Figshare()  # No token needed for public dataset

        self.curation_dict = config_dict['curation']

        self.root_directory = \
            self.curation_dict[self.curation_dict['parent_dir']]
        self.published_folder = self.curation_dict['folder_published']

        # Search for path
        p_dir = Path(self.root_directory) / self.published_folder
        list_paths = list(p_dir.glob(f'*{self.article_id}'))
        if len(list_paths) == 0:
            self.log.warning(
                f"No curated dataset found in {self.published_folder}.")
            self.log.warning("Exiting !!!")
            raise ValueError
        if len(list_paths) > 1:
            self.log.warning(
                f"More than one paths found in {self.published_folder}.")
            self.log.warning("Exiting !!!")
            raise ValueError

        self.folder_name = Path(list_paths[0])
        self.version_dir = self.folder_name / f"v{self.version_no:02}"
        if self.version_dir.exists():
            self.log.info("Article and version found!")
        else:
            self.log.warning("Version not found.")
            self.log.warning("Exiting !!!")
            raise OSError

        # Retrieve Figshare metadata and save metadata
        self.article_metadata = self.get_metadata()

    def get_metadata(self) -> dict:
        """Retrieve Figshare metadata from public API"""
        article_metadata = self.fs.get_article_details(self.article_id,
                                                       self.version_no)
        return article_metadata

    def save_metadata(self):
        """Write JSON file containing Figshare metadata"""
        out_file_prefix = f"published_{self.article_id}"
        metadata.save_metadata(self.article_metadata,
                               out_file_prefix,
                               metadata_source='FIGSHARE',
                               root_directory=self.version_dir,
                               metadata_directory='METADATA',
                               log=self.log)
