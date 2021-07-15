from pathlib import Path

from logging import Logger
from typing import List, Dict

import pandas as pd

from redata.commons.logger import log_stdout

# LD-Cool-P specific
from figshare.figshare import Figshare
from ..config import config_default_dict
from ..curation import metadata
from ..curation.inspection import checksum

# Wildcards for globbing hidden files
HIDDEN_FILES = ['*DS_Store', '.*.docx', '.*.pdf']


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
        self.data_path = self.curation_dict['folder_copy_data']  # DATA
        self.original_data_path = self.curation_dict['folder_data']  # ORIGINAL_DATA
        self.metadata_path = self.curation_dict['folder_metadata']  # METADATA

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
            self.log.warning("Version not found!")
            self.log.warning("Exiting !!!")
            raise OSError

        # Ensure that METADATA folder exists (support for very old deposits)
        m_path = self.version_dir / self.metadata_path
        if not m_path.exists():
            self.log.info(f"{self.metadata_path} NOT found!")
            self.log.info(f"Creating: {self.metadata_path}")
            m_path.mkdir()

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
                               metadata_directory=self.metadata_path,
                               log=self.log)

    def check_files(self, save_files: bool = False) -> pd.DataFrame:
        """Performs checksum verification on each file"""

        if self.article_metadata['is_embargoed']:
            self.log.warning(
                f"Embargoed files! File checking is not possible at this time")
            self.log.warning(
                f"Embargo date: {self.article_metadata['embargo_date']}")
            raise SystemExit("NOTE: Embargoed datasets NOT supported at this point")
        else:
            summary_list = []  # Initialize
            files_list: List[Dict] = self.article_metadata['files']
            d_dir = self.version_dir / self.data_path
            o_dir = self.version_dir / self.original_data_path
            for n, file_dict in enumerate(files_list):
                filename = file_dict['name']
                glob_list = list(d_dir.glob(filename))

                data_location = ''
                if len(glob_list) == 0:
                    try:
                        t_path = list(o_dir.glob(filename))[0]
                        if not t_path.exists():
                            raise FileNotFoundError
                        else:
                            self.log.info(
                                f"{filename} found in {self.original_data_path}")
                            data_location = self.original_data_path
                    except (IndexError, FileNotFoundError):
                        self.log.warning(f"File not found: {filename}")
                else:
                    t_path = glob_list[0]
                    self.log.info(
                        f"{filename} found in {self.data_path}")
                    data_location = self.data_path

                checksum_flag = \
                    checksum.check_md5(t_path, file_dict['supplied_md5'],
                                       log=log_stdout())

                summary_list.append({
                    'name': filename,
                    'data_location': data_location,
                    'checksum_status': checksum_flag,
                })
                summary_list[n].update(file_dict)

            if save_files:
                out_file_prefix = f'checksum_summary_{self.article_id}'
                metadata.save_metadata(summary_list, out_file_prefix,
                                       metadata_source='CHECKSUM',
                                       root_directory=self.version_dir,
                                       metadata_directory=self.metadata_path,
                                       save_csv=True, log=self.log)

            df = pd.DataFrame.from_dict(summary_list, orient='columns')
            return df

    def make_symbolic_links(self, df):
        """Construct symbolic links in DATA from ORIGINAL_DATA as needed

        :param df: pandas DataFrame from ``check_files()``
        """

        # Get list of those in ORIGINAL_DATA
        df_symlink = df.loc[df['data_location'] == self.original_data_path]

        if df_symlink.empty:
            self.log.info(f"All files are in {self.data_path}")
            self.log.info("No symbolic links are needed! :-)")
        else:
            for index, row in df_symlink.iterrows():
                self.log.info(f"{index}. Creating symbolic link for {row['name']}")
                data_path = self.version_dir / self.data_path / row['name']
                data_path.symlink_to(f"../{self.original_data_path}/{row['name']}")

    def delete_old_readme_files(self):
        """Find and remove all old README.txt files in DATA"""

        d_dir = self.version_dir / self.data_path
        files_find_list = list(d_dir.glob('README_????-??-??T*.txt'))
        if len(files_find_list) == 0:
            self.log.info("No old README.txt files found! :-)")
        else:
            self.log.info(f"Old README.txt files found, N={len(files_find_list)}!")
            self.delete_files(files_find_list)

    def delete_hidden_files(self):
        """Find and remove all hidden files. See ``HIDDEN_FILES`` wildcards"""
        hidden_files_list = []
        for hidden in HIDDEN_FILES:
            file_find = list(self.version_dir.rglob(hidden))
            if len(file_find) > 0:
                hidden_files_list.extend(file_find)

        if len(hidden_files_list) == 0:
            self.log.info("No hidden files found! :-)")
        else:
            self.log.info(f"Hidden files found, N={len(hidden_files_list)}!")
            self.delete_files(hidden_files_list)

        return hidden_files_list

    def delete_files(self, files_list: List[Path]):
        """Delete list of files if response to prompt is yes"""
        for f_path in files_list:
            self.log.info(f_path.relative_to(self.version_dir))
        self.log.info("PROMPT: Do you you wish to delete all of these files")
        src_input = input("PROMPT: Type 'yes'. Anything else will skip : ")
        self.log.info(f"RESPONSE: {src_input}")
        if src_input.lower() == 'yes':
            for f_path in files_list:
                self.log.info(f"Removing: {f_path.relative_to(self.version_dir)}")
                f_path.unlink()
        else:
            self.log.info("Not deleting files.")
