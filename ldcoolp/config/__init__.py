import configparser

from .. import config_file

config = configparser.ConfigParser()
config.read(config_file)

# Local or remote servrer
source = config.get('curation', 'source')

# Curation root folder
root_directory_main = config.get('curation', f'{source}_path')

# Curation primary folders
folder_ual_rdm = config.get('curation', 'folder_ual_rdm')
folder_data = config.get('curation', 'folder_data')
folder_copy_data = config.get('curation', 'folder_copy_data')

# Folders for high-level curation workflow
todo_folder = config.get('curation', 'folder_todo')
underreview_folder = config.get('curation', 'folder_underreview')
reviewed_folder = config.get('curation', 'folder_reviewed')
published_folder = config.get('curation', 'folder_published')
rejected_folder = config.get('curation', 'folder_rejected')

# Curation Review Report URL
report_url = config.get('curation', 'report_url')

# Flag to copy README in folder_copy_data
readme_copy_flag = config.getboolean('curation', 'readme_copy')

# Filename for README markdown template
readme_template = config.get('curation', 'readme_template')

# Figshare API
api_token = config.get('global', 'api_token')

# Flag for using different Figshare API endpoint (stage vs production)
stage_flag = config.getboolean('global', 'stage')

# Qualtrics API settings
qualtrics_survey_id = config.get('curation', 'qualtrics_survey_id')
qualtrics_token = config.get('curation', 'qualtrics_token')
qualtrics_dataCenter = config.get('curation', 'qualtrics_dataCenter')

# Qualtrics URLs
qualtrics_download_url = config.get('curation', 'qualtrics_download_url')
qualtrics_generate_url = config.get('curation', 'qualtrics_generate_url')
