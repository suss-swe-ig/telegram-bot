from typing import List, Tuple

import telebot
from telebot.async_telebot import AsyncTeleBot
import shelve
import logging

def setupBot(token:str, admins:List[str], logger:logging.Logger, dbname:str) -> AsyncTeleBot:
    bot = AsyncTeleBot(token)
    db = shelve.open(dbname)
    addHandlers(bot, admins, db, logger)
    return bot

def getName(message: telebot.types.Message) -> str:
    name = message.from_user.username
    if name == "":
        name = message.from_user.full_name
    return name

def addHandlers(bot: AsyncTeleBot, admins: List[str], db: shelve.Shelf, logger:logging.Logger):

    @bot.message_handler(commands=['start','welcome'])
    async def welcome(message:telebot.types.Message) -> telebot.types.Message:
        await bot.reply_to(message, f"hello {message.from_user.full_name}")
    
    @bot.message_handler(commands=['add'])
    async def add(message:telebot.types.Message) -> telebot.types.Message:
        """
        /add [unitcode] [link] [title]
        """
        success = False
        if message.from_user.username in admins:
            tokens = message.text.split()
            unitcode = tokens[1].upper()
            unitname = " ".join(tokens[3:])
            link = tokens[2]
            if unitcode[:3].isalpha() and unitcode[3:].isnumeric():
                if link.startswith("https://t.me/"):
                    if len(unitname) > 0:
                        db[unitcode] = (unitname, link)
                        db.sync()
                        success = True
                        logger.info(f"{message.from_user.username} added {unitcode}: {unitname}")
                        await bot.reply_to(message, f"Success. Added {unitcode}: {unitname}")
                    else:
                        logger.error(f"{message.from_user.username} attempted to add {unitcode} without name")
                else:
                    logger.error(f"{message.from_user.username} attempted to add invalid telegram invitation link for {unitcode}")
            else:
                logger.error(f"{message.from_user.username} attempted to add malformed unit code {unitcode}")
        else:
            logger.error(f"Unauthorised user f{getName(message)} attempted to perform {message.text}")
            await bot.reply_to(message, "Error: Unauthorised user")
        if not success:
            await bot.reply_to(message, f"Fail")
   
