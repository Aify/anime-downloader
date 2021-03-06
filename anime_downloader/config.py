import click
import os
import errno
import json

APP_NAME = 'anime downloader'
APP_DIR = click.get_app_dir(APP_NAME)
DEFAULT_CONFIG = {
    'dl': {
        'url': False,
        'player': None,
        'skip_download': False,
        'download_dir': '.',
        'quality': '720p',
        'force_download': False,
        'log_level': 'INFO',
    },
    'watch': {
        'quality': '720p',
        'log_level': 'INFO',
    }
}


class _Config:
    CONFIG_FILE = os.path.join(APP_DIR, 'config.json')

    def __init__(self):
        try:
            os.makedirs(APP_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        if not os.path.exists(self.CONFIG_FILE):
            self._write_default_config()
            self._CONFIG = DEFAULT_CONFIG
        else:
            self._CONFIG = self._read_config()

    @property
    def CONTEXT_SETTINGS(self):
        return dict(
            default_map=self._CONFIG
        )

    def _write_config(self, config_dict):
        with open(self.CONFIG_FILE, 'w') as configfile:
            json.dump(config_dict, configfile, indent=4, sort_keys=True)

    def _read_config(self):
        with open(self.CONFIG_FILE, 'r') as configfile:
            conf = json.load(configfile)
        return conf

    def _write_default_config(self):
        self._write_config(DEFAULT_CONFIG)


Config = _Config()
