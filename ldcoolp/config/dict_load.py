import configparser
import ast


def qualtrics_check(config_dict: dict):
    """
    Perform Qualtrics checks on config file

    :param config_dict: Dictionary containing all LD-Cool-P configuration
    """

    qualtrics_err = 0
    qualtrics_err_source = []

    if 'qualtrics' in config_dict:
        if isinstance(config_dict['qualtrics']['survey_id'], list):
            ref_size = len(config_dict['qualtrics']['survey_id'])
            for key in ['survey_shortname', 'survey_email']:
                if len(config_dict['qualtrics'][key]) != ref_size:
                    qualtrics_err += 1
                    qualtrics_err_source.append(key)
        else:
            print("Not survey_id in config file")
    else:
        print("Not qualtrics settings in config file")

    if qualtrics_err != 0:
        str_join = ', '.join(qualtrics_err_source)
        print(f"ERROR: Number of items incorrect in: {str_join}")
        raise configparser.ParsingError(source=str_join)


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

    # Check Qualtrics input
    qualtrics_check(config_dict)

    return config_dict
