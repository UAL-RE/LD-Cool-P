from os.path import exists, join
from os import makedirs

from urllib.request import urlretrieve

from ldcoolp.admin import permissions
from redata.commons.logger import log_stdout

from ..config import config_default_dict


def review_report(depositor_name='', curation_dict=config_default_dict['curation'], log=None):
    """
    Purpose:
      Retrieve Curation Review Report and save on curation server
    """

    if isinstance(log, type(None)):
        log = log_stdout()

    log.info("")
    log.info("** CREATING CURATION REVIEW REPORT **")

    root_directory_main = curation_dict[curation_dict['parent_dir']]
    todo_folder = curation_dict['folder_todo']
    folder_ual_rdm = curation_dict['folder_ual_rdm']
    report_url = curation_dict['report_url']

    staging_directory = join(root_directory_main, todo_folder)

    # Complete path to UAL_RDM folder
    out_path = join(staging_directory, depositor_name, folder_ual_rdm)
    if not exists(out_path):
        log.info(f"Creating folder : {out_path}")
        makedirs(out_path, mode=0o2770, exist_ok=True)
    else:
        log.warn(f"!!!! Folder exists, not creating : {out_path}")

    # MS-Word document filename
    simplify_name = depositor_name.replace('/v', '_v')
    filename = 'ReDATA-DepositReview_{}.docx'.format(simplify_name)
    out_file = join(out_path, filename)

    # Write file
    if not exists(out_file):
        log.info(f"Saving ReDATA Curation Report to: {out_path}")
        log.info(f"Saving as : {filename}")
        urlretrieve(report_url, out_file)
        permissions.curation(out_path)
    else:
        log.info(f"!!!! ReDATA Curation Report exists in {out_path} !!!!")
        log.info("!!!! Will not override !!!!")
