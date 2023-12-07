
import os
import glob
from .config.system_config import load_sys_config
from .config.radar_config import load_radar_config

conf_dir = os.environ.get('CONFIG_PATH')

if conf_dir is not None:
    config_file = os.path.join(conf_dir,"sysconfig.yaml")
    search_path = os.path.join(conf_dir,"radars","*.yaml")
else:
    raise RuntimeError("CONFIG_PATH is net set, see ropac README.md for info")

system_config = load_sys_config(config_file)
radar_files = glob.glob(search_path)
radar_config = load_radar_config(radar_files)

from .odim_moment_object import Moment
from .odim_elevation_object import Elevation
from .odim_volume_object import PolarVolume

