from typing import Union, Dict, Any

import config


def params_from_config(section: str) -> Union[Dict[str, Any], str]:
    return getattr(config, section, None)
