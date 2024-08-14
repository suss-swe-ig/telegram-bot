from typing import List, Tuple
from dotenv import dotenv_values

class ConfigException(Exception):
    pass

def readConfig() -> Tuple[str, List[str], str]:
    config = dotenv_values(".env")
    try:
        token = config["TOKEN"]
    except KeyError:
        raise ConfigException("Missing API Token")
    try:
        admins = config["ADMINS"].split(",")
    except KeyError:
        raise ConfigException("Missing Admins List")
    try:
        database = config["DATABASE"]
    except KeyError:
        database = "database.db"
    return token, admins, database
