from typing import List, Tuple

import telebot
from telebot.async_telebot import AsyncTeleBot
import shelve
import logging

def setupBot(token:str, admins:List[str], logger:logging.Logger, dbname:str) -> AsyncTeleBot:
    bot = AsyncTeleBot(token)
    db = shelve.open(dbname)
    _addHandlers(bot, admins, db, logger)
    return bot

def _getName(message: telebot.types.Message) -> str:
    name = message.from_user.username
    if name == "":
        name = message.from_user.full_name
    return name

def _validUnitCode(unitCode:str) -> bool:
    return len(unitCode) == 6 and unitCode[:3].isalpha() and unitCode[3:].isnumeric()

def _addHandlers(bot: AsyncTeleBot, admins: List[str], db: shelve.Shelf, logger:logging.Logger) -> None:

    @bot.message_handler(commands=['start','welcome'])
    async def welcome(message:telebot.types.Message) -> telebot.types.Message:
        """
        /start      Says hi to user
        /welcome    Says hi to user
        """
        await bot.reply_to(message, f"hello {message.from_user.full_name}. Enter /help to see what commands are available.")
    
    @bot.message_handler(commands=['admins'])
    async def adminlist(message:telebot.types.Message) -> telebot.types.Message:
        """
        /admins     retrieve the list of administrators
        """
        msg = f"The administrator is @{admins[0]}"
        if len(admins) > 1:
            msg = f"The administrators are {", ".join(["@" + admin for admin in admins])}."
        msg = "Contact an administrator to add or remove a telegram chat group. \n\n" + msg
        await bot.reply_to(message, msg)

    @bot.message_handler(commands=['add'])
    async def add(message:telebot.types.Message) -> telebot.types.Message:
        """
        /add [unitCode] [link] [title]   Add a telegram group
        """
        success = False
        msg = ""
        if message.from_user.username in admins:
            tokens = message.text.split()
            unitCode = tokens[1].upper()
            unitName = " ".join(tokens[3:])
            link = tokens[2]
            if _validUnitCode(unitCode):
                if link.startswith("https://t.me/"):
                    if len(unitName) > 0:
                        db[unitCode] = (unitName, link)
                        db.sync()
                        success = True
                        logger.info(f"{message.from_user.username} added {unitCode} {unitName}")
                        await bot.reply_to(message, f"Success. Added {link} for {unitCode} {unitName}")
                    else:
                        logger.error(f"{message.from_user.username} attempted to add {unitCode} without name")
                        msg = f"unit name not included for {unitCode}"
                else:
                    logger.error(f"{message.from_user.username} attempted to add invalid telegram invitation link for {unitCode}")
                    msg = f"Invalid telegram invitation link {link}"
            else:
                logger.error(f"{message.from_user.username} attempted to add {unitCode} is a malformed unit code.")
                msg = f"{unitCode} is a malformed unit code."
        else:
            logger.error(f"Unauthorised user f{_getName(message)} attempted to perform {message.text}")
            msg = f"{_getName(message)} is Unauthorised user"
        if not success:
            await bot.reply_to(message, f"Fail because {msg}")
   
    @bot.message_handler(commands=["rm"])
    async def remove(message:telebot.types.Message) -> telebot.types.Message:
        """
        /rm [unitCode]      removes a telegram group for that unit code.
        """
        success = False
        msg = ""
        if message.from_user.username in admins:
            tokens = message.text.split()
            unitCode = tokens[1].upper()
            if _validUnitCode(unitCode):
                if unitCode in db:
                    unitName, link = db[unitCode]
                    success = True
                    del db[unitCode]
                    logger.info(f"{message.from_user.username} removed {unitCode}")
                    await bot.reply_to(message, f"Success. {unitCode} removed.\n\n To re-add, run:\n\n /add {unitCode} {link} {unitName}")
                else:
                    msg = f"No known telegram group for {unitCode}"
            else:
                msg = f"{unitCode} is a malformed unit code."
        else:
            msg = f"{_getName(message)} is an unauthorised user"
        if not success:
            await bot.reply_to(message, f"Fail because {msg}")
    
    @bot.message_handler(commands = ["get"])
    async def get(message:telebot.types.Message) -> telebot.types.Message:
        """
        /get all            return all telegram invitation links
        /get [unitCode]     return telegram invitation link for a specific unit
        """
        success = False
        msg = ""
        tokens = message.text.split()
        unitCode = tokens[1].upper()
        if unitCode == "ALL":
            if len(db) == 0:
                await bot.reply_to(message, "No telegram groups available")
            else:
                unitCodes = sorted([unitCode for unitCode in db])
                prefix = unitCodes[0][:3]
                lines = []
                for unitCode in unitCodes:
                    if unitCode[:3] != prefix:
                        await bot.reply_to(message, "\n".join(lines))
                        lines = []
                        prefix = unitCode[:3]
                    unitName, link = db[unitCode]
                    lines.append(f"{unitCode} {unitName}")
                    lines.append(link)
                    lines.append("")
                if len(lines) > 0:
                    await bot.reply_to(message, "\n".join(lines))
                    lines = []
            success = True
        elif _validUnitCode(unitCode):
            if unitCode in db:
                success = True
                unitName, link = db[unitCode]
                await bot.reply_to(message, f"Click {link} to join: \n{unitCode} {unitName}")
            else:
                msg = f"no known telegram group for {unitCode}."
        else:
            msg = f"{unitCode} is a malformed unit code."
        if not success:
            await bot.reply_to(message, f"Fail because {msg}")

    @bot.message_handler(commands = ["update"])
    async def update(message:telebot.types.Message) -> telebot.types.Message:
        """
        /update [unit code] link [new link]         update the th
        /update [unit code] name [new unit name]
        """
        success = False
        msg = ""
        tokens = message.text.split()
        if len(tokens) < 4:
            msg = "the update command has missing arguments"
        elif message.from_user.username not in admins:
            msg = f"{message.from_user.username} is not an administrator."
            logger.error(f"Unauthorised user {_getName(message)} attempted to perform an update.")
        else:
            unitCode = tokens[1].upper()
            mode = tokens[2].upper()
            if _validUnitCode(unitCode):
                if mode == "LINK":
                    link = tokens[3]
                    if link.startswith("https://t.me/"):
                        if unitCode in db:
                            success = True
                            unitName, _ = db[unitCode]
                            db[unitCode] = (unitName, link)
                            logger.info(f"{_getName(message)} updated link for {unitCode}")
                            await bot.reply_to(message, f"Success. Updated link for {unitCode}")
                        else:
                            msg = f"{unitCode} does not exist in database."
                    else:
                        msg = f"invalid telegram invitation link {link} for {unitCode}"
                elif mode == "NAME":
                    if unitCode in db:
                        unitName = " ".join(tokens[3:])
                        _, link = db[unitCode]
                        db[unitCode] = (unitName, link)
                        success = True
                        logger.info(f"{message.from_user.username} updated name for {unitCode}")
                        await bot.reply_to(message, f"Suuccess. Updated name for {unitCode}")
                    else:
                        msg = f"{unitCode} does not exist in database."
                else:
                    msg = "update command didn't specify link or name"
            else:
                msg = f"{unitCode} is a malformed unit code."
        if not success:
            await bot.reply_to(message, f"Fail because {msg}")

    @bot.message_handler(commands = ["help"])
    async def help(message:telebot.types.Message) -> telebot.types.Message:
        """
        /help   display all commands available to the user
        """
        pass