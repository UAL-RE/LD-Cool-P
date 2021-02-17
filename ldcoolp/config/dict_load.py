import configparser
import ast


def dict_load(config_file):
    """
    Purpose:
      Read in a config INI file using configparser and return a dictionary
      with sections and options

    :param config_file: str. Full/relative path of configuration file

    :return config_dict: dict of dict with hierarchy of sections follow by options
    """

    config = configparser.ConfigParser()
    config.read(config_file)

    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for option in config.options(section):
            option_input = config.get(section, option)
            if option_input in ['True', 'False']:
                config_dict[section][option] = config.getboolean(section, option)
            else:
                config_dict[section][option] = option_input
                # Re-process if value can be interpreted as a list
                # (allows for multiple values for key)
                try:
                    ast_process = ast.literal_eval(option_input)
                    if isinstance(ast_process, list):
                        config_dict[section][option] = ast_process
                except (ValueError, SyntaxError) as e:
                    pass
    return config_dict
