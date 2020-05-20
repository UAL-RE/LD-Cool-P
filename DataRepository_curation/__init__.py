from os import path

co_path = path.dirname(__file__)

config_dir  = path.join(co_path, 'config/')
config_file = 'default_ini'
config_file = path.join(config_dir, config_file)
