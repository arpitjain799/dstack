from typing import Dict, List

from dstack.backend.aws.config import AWSConfig
from dstack.backend.hub.config import HUBConfig
from dstack.core.config import BackendConfig


def list_config() -> List[BackendConfig]:
    configs = [cls() for cls in BackendConfig.__subclasses__()]  # pylint: disable=E1101
    return configs


def dict_config() -> Dict[str, BackendConfig]:
    configs = [cls() for cls in BackendConfig.__subclasses__()]  # pylint: disable=E1101
    names = {}
    for config in configs:
        if config.configured:
            names[config.name] = config

    return names
