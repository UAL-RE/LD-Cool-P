from ldcoolp import logger

from os.path import join
from os import remove

import logging
from datetime import date

today = date.today()
log_dir = ''
logfile = f'testlog.{today.strftime("%Y-%m-%d")}.log'


def test_LogClass():

    log0 = logger.LogClass(log_dir, logfile).get_logger()

    log0.info("Print INFO test")
    log0.debug("Print DEBUG test")
    log0.warning("Print WARNING test")

    assert isinstance(log0, logging.Logger)

    # Delete log file
    remove(join(log_dir, logfile))


def test_log_stdout():
    log0 = logger.log_stdout()

    log0.info("Print INFO test")
    log0.debug("Print DEBUG test")
    log0.warning("Print WARNING test")

    assert isinstance(log0, logging.Logger)


def test_get_hostname():

    sys_info = logger.get_user_hostname()

    assert isinstance(sys_info, dict)

    for key in ['user', 'hostname', 'ip', 'os']:
        assert key in sys_info.keys()
