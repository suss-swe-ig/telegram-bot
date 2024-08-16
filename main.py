import asyncio
import logging 
import shelve

import config
import service

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
        database = shelve.open(dbname)
        svc = service.Service(token, admins, logger, database)
        svc.run()
