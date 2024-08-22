import logging 
import shelve

import config
import service

import persistence

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    try:
        token, admins, dbname = config.readConfig()
    except config.ConfigException as e:
        logger.error(e)
        logger.info("suss-telegram-groups bot terminates")
    else:
        logger.info("suss-telegram-groups bot starts")
        persistence.setup(dbname, admins)
        service.setup(token, logger)
        service.run()
