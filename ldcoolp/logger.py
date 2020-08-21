import sys
from os.path import join

import logging
formatter = logging.Formatter('%(asctime)s - %(levelname)8s: %(message)s', "%H:%M:%S")


class LogClass:
    """
    Purpose:
      Main class to log information to stdout and ASCII logfile

    Note [1]: This code is identical to the one used in ReQUIAM_csv:
      https://github.com/ualibraries/ReQUIAM_csv

    Note [2]: Logging level is set for DEBUG for file and INFO for stdout

    To use:
    log = LogClass(log_dir, logfile).get_logger()

    Parameters:
      log_dir: Relative path for exported logfile directory
      logfile: Filename for exported log file
    """

    def __init__(self, log_dir, logfile):
        self.LOG_FILENAME = join(log_dir, logfile)

    def get_logger(self):
        file_log_level = logging.DEBUG  # This is for file logging
        log = logging.getLogger(self.LOG_FILENAME)
        if not getattr(log, 'handler_set', None):
            sh = logging.StreamHandler(sys.stdout)
            sh.setFormatter(formatter)
            sh.setLevel(logging.info)  # Only at INFO level
            log.addHandler(sh)

            fh = logging.FileHandler(self.LOG_FILENAME)
            fh.setLevel(file_log_level)
            fh.setFormatter(formatter)
            log.addHandler(fh)

            log.handler_set = True
        return log


def log_stdout():
    log_level = logging.INFO
    log = logging.getLogger()
    log.setLevel(log_level)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    log.addHandler(sh)
    return log
