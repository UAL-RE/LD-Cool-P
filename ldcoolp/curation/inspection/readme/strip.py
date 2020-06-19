from os.path import exists
import shutil

import numpy as np

from ....admin import permissions

from . import default_readme_path


def html_comments(lines0, change):
    """
    Purpose:
      Remove HTML comments from README.txt file

    :param lines0: list containing text from open()
    :param change: int that indicates whether changes have been implemented

    :return lines: np.array containing text with HTML comments stripped out
    :return change: Updated change (+1) if changes are made
    """

    lines = np.array(lines0)

    # Strip out HTML comments noted via <!--- to -->
    html_comment_beg = [xx for xx in range(len(lines0)) if '<!---' in lines0[xx][0:5]]
    html_comment_end = [xx for xx in range(len(lines0)) if '-->' in lines0[xx][0:3]]

    if len(html_comment_beg) != 0:
        print("HTML comments found. Stripping...")
        change += 1

        list_range = [[*range(beg, end+1)] for beg, end in
                      zip(html_comment_beg, html_comment_end)]

        # Concatenate list_range into a single list of index to remove
        remove_index = [j for i in list_range for j in i]

        # Easier to use numpy to remove a list of index than using list remove()
        lines = np.delete(lines, remove_index)
    else:
        print("No HTML comments found!")

    return lines, change


def beginning(lines, change):
    """
    Purpose:
      Strip extraneous text above first heading

    :param lines: np.array containing text from open()
    :param change: int that indicates whether changes have been implemented

    :return lines: np.array containing text with extraneous text stripped out
    :return change: Updated change (+1) if changes are made
    """

    head_i = [i for i in range(len(lines)) if lines[i][0:4] == '----']
    if len(head_i) == 0:
        print("WARNING: No section heading found!!!...")
    else:
        if head_i[0] != 0:
            print("Excess white space found at top. Stripping...")
            change += 1
            lines = np.delete(lines, range(head_i[0]))
        else:
            print("No excess white space found at top!")

    return lines, change


def main(depositor_name):

    README_file_default, _ = default_readme_path(depositor_name)

    f1 = open(README_file_default, 'r')
    lines0 = f1.readlines()
    f1.close()

    change = 0

    lines, change = html_comments(lines0, change)

    lines, change = beginning(lines, change)

    if change:
        orig_file = README_file_default.replace('.txt', '.orig.txt')
        if not exists(orig_file):
            shutil.copy(README_file_default, orig_file)
            permissions.curation(orig_file)
        else:
            print("README original copy exists! Not overwriting!")

        f2 = open(README_file_default, 'w')
        f2.writelines(lines)
        f2.close()
        permissions.curation(README_file_default)
