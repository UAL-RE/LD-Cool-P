from os.path import exists, join
from os import makedirs

from urllib.request import urlretrieve

from ldcoolp.admin import permissions

from ..config import config_default_dict


def review_report(depositor_name='', curation_dict=config_default_dict['curation']):
    """
    Purpose:
      Retrieve Curation Review Report and save on curation server
    """

    root_directory_main = curation_dict[curation_dict['parent_dir']]
    todo_folder = curation_dict['folder_todo']
    folder_ual_rdm = curation_dict['folder_ual_rdm']
    report_url = curation_dict['report_url']

    staging_directory = join(root_directory_main, todo_folder)

    # Complete path to UAL_RDM folder
    out_path = join(staging_directory, depositor_name, folder_ual_rdm)
    if not exists(out_path):
        makedirs(out_path, mode=0o777, exist_ok=True)

    # MS-Word document filename
    filename = 'ReDATA-DepositReview_{}.docx'.format(depositor_name)
    out_file = join(out_path, filename)

    # Write file
    if not exists(out_file):
        print("Saving ReDATA Curation Report to: {}".format(out_path))
        print("Saving as : {}".format(filename))
        urlretrieve(report_url, out_file)
        permissions.curation(out_path)
    else:
        print("!!!! ReDATA Curation Report exists in {} !!!!".format(out_path))
        print("!!!! Will not override !!!!")
