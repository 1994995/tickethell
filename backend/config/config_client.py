import os
from configparser import ConfigParser
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ? If I'm having a class like this should this manage EVERY config required or is that silly for something like this
class ConfigClient:
    _config = None

    @classmethod
    def load_config(cls):

        # ? Might be safer to wrap in `os.path.abspath`
        # ? If deployed might also need a `Frozen` check but its been a while since I've had to deal with that
        base_path = Path(__file__).parent.absolute()
        print(base_path)
        config = ConfigParser()
        with open(os.path.join(base_path, "config.ini"), 'r') as f:
            config.read_file(f)
            cls._config = config

    @classmethod
    def get_property(cls, key: str, section: str = "DEFAULT", default=None):
        if cls._config is None:
            print(f'LOADING CONFIG')
            cls.load_config()

        return cls._config[section].get(key, default)