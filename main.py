import asyncio
import logging 
import config
import bot

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    try:
        token, admins, database = config.readConfig()
    except config.ConfigException as e:
        logger.error(e)
        logger.info("suss-telegram-groups bot terminates")
    else:
        suss_telegram_groups_bot = bot.setupBot(token, admins, logger, database)
        asyncio.run(suss_telegram_groups_bot.polling())
