from os import path

__version__ = "1.0.2"

CODE_NAME = "LD-Cool-P"

co_path = path.dirname(__file__)

##############################################
# Instructions                               #
# Modify [config_dir] and [main_config_file] #
# to specify correct configuration file      #
##############################################
config_dir       = path.join(co_path, 'config/')
main_config_file = 'default.ini'
config_file      = path.join(config_dir, main_config_file)  # Contains full path to main configuration file
