from typing import Any

from .. import config_file
from .dict_load import dict_load

config_default_dict: dict[str, dict[str, Any]] = dict_load(config_file)
