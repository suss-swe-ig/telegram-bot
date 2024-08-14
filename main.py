import logging 
import config
import bot

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    try:
        token, admins = config.readConfig()
    except config.ConfigException as e:
        logger.error(e)
        logger.info("suss-telegram-groups bot terminates")
    else:
        b = bot.getBot(token, admins, logger)
        b.infinity_polling()
