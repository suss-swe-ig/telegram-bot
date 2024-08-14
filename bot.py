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

def validUnitCode(unitcode:str) -> bool:
    return len(unitcode) == 6 and unitcode[:3].islapha() and unitcode[3:].isnumeric()

def addHandlers(bot: AsyncTeleBot, admins: List[str], db: shelve.Shelf, logger:logging.Logger) -> None:

    @bot.message_handler(commands=['start','welcome'])
    async def welcome(message:telebot.types.Message) -> telebot.types.Message:
        await bot.reply_to(message, f"hello {message.from_user.full_name}")
    
    @bot.message_handler(commands=['add'])
    async def add(message:telebot.types.Message) -> telebot.types.Message:
        """
        /add [unitcode] [link] [title]
        """
        success = False
        msg = ""
        if message.from_user.username in admins:
            tokens = message.text.split()
            unitcode = tokens[1].upper()
            unitname = " ".join(tokens[3:])
            link = tokens[2]
            if validUnitCode(unitcode):
                if link.startswith("https://t.me/"):
                    if len(unitname) > 0:
                        db[unitcode] = (unitname, link)
                        db.sync()
                        success = True
                        logger.info(f"{message.from_user.username} added {unitcode}: {unitname}")
                        await bot.reply_to(message, f"Success. Added {link} for {unitcode}: {unitname}")
                    else:
                        logger.error(f"{message.from_user.username} attempted to add {unitcode} without name")
                        msg = f"unit name not included for {unitcode}"
                else:
                    logger.error(f"{message.from_user.username} attempted to add invalid telegram invitation link for {unitcode}")
                    msg = f"Invalid telegram invitation link {link}"
            else:
                logger.error(f"{message.from_user.username} attempted to add malformed unit code {unitcode}")
                msg = "Malformed unit code {unitcode}"
        else:
            logger.error(f"Unauthorised user f{getName(message)} attempted to perform {message.text}")
            msg = f"{getName(message)} is Unauthorised user"
        if not success:
            await bot.reply_to(message, f"Fail because {msg}")
   
    @bot.message_handler(commands=["rm"])
    async def remove(message:telebot.types.Message) -> telebot.types.Message:
        """
        /rm [unitcode]
        """
        success = False
        msg = ""
        if message.from_user.username in admins:
            tokens = message.text.split()
            unitcode = tokens[1].upper()
            if validUnitCode(unitcode):
                if unitcode in db:
                    success = True
                    del db[unitcode]
                    logger.info(f"{message.from_user.username} removed {unitcode}")
                    await bot.reply_to(message, f"Success. {unitcode} removed")
                else:
                    msg = "No telegram group for unit code {unitcode}"
            else:
                msg = "Malformed unit code"
        else:
            msg = f"{getName(message)} is Unauthorised user"
        if not success:
            await bot.reply(message, f"Fail because {msg}")
    
    @bot.message_handler(commands = ["get"])
    async def get(message:telebot.types.Message) -> telebot.types.Message:
        """
        /get all            return all telegram invitation links
        /get [unitcode]     return telegram invitation link for a specific unit
        """
        success = False
        msg = ""
        tokens = message.text.split()
        unitcode = tokens[1].upper()
        if unitcode == "ALL":
            unitcodes = sorted([key for key in db])
            if len(unitcodes) == 0:
                bot.reply_to(message, "No telegram invitation links available")
            else:
                prev = unitcodes[0][:3]
                units = []
                for u in unitcodes:
                    if prev != u[:3]:
                        bot.reply_to(message, "\n".join(units))
                        units = []
                    units.append(" ".join(db[u]))
                    units.append("")
                    prev = u
                if len(units) > 0:
                    bot.reply_to(message, "\n".join(units))
        elif validUnitCode(unitcode):
            if unitcode in db:
                success = True
                unitname, link = db[unitcode]
                await bot.reply_to(message, f"Click {link} to join {unitcode}: {unitname}")
            else:
                msg = "No telegram group for unit code {unitcode}"
        else:
            msg = "Malformed unit code"
        if not success:
            await bot.reply(message, f"Fail because {msg}")

