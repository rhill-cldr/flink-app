import os
from pyhocon import ConfigFactory
from dataclasses import dataclass
from dacite import from_dict
from . atk_conf import AtkConf
from . defaults import FlinkConf
from . defaults import YarnConf


@dataclass
class Defaults:
    flink: FlinkConf
    yarn: YarnConf

@dataclass
class BaseConf:
    atk: AtkConf
    defaults: Defaults

def load_config(path_config=None):
    if path_config is None:
        path_config = os.environ.get("ATK_PATH_CONFIG")
    return from_dict(BaseConf, ConfigFactory.parse_file(path_config))

