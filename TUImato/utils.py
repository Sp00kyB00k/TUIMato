import tomlkit
import os 

def load_config(file_name: str) -> dict:
    try:
        if not os.path.exists(file_name):
            return {}
        with open(file_name, "rb") as config_file:
            configuration = tomli.load(config_file)
        return configuration
    except (FileNotFoundError, PermissionError, tomli.TOMLDecodeError):
        return {}


def write_config()
