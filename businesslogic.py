from typing import List
from shelve import Shelf
from logging import Logger

import telebot 
from telebot.async_telebot import AsyncTeleBot
import telebot.async_telebot

from persistence import getDatabase, TelegramGroup
from persistence import MalformedUnitCodeException, NoTelegramGroupException, BadTelegramLinkException, BadUnitNameException

class NonAdminUserException(Exception):
    def __init__(self, username, fullname):
        super().__init__(f"{username} {fullname} is not an administrator")

class User:
    def __init__(self, username:str, fullname:str, logger:Logger):
        self._username = username
        self._fullname = fullname
        self._db = getDatabase()
        self._logger = logger
    
    def isAdmin(self) -> bool:
        return self._username in self._db.getAdmins()

    def welcome(self, message:telebot.types.Message) -> List[str]:
        return ["\n".join([
            f"hello {message.from_user.full_name},"
            "",
            "",
            "Enter /help to see what commands are available."
        ])]

    def get(self, message:telebot.types.Message) -> List[str]:
        tokens = message.text.split()
        unitCode = tokens[1].upper()
        if unitCode == "ALL":
            tgs = sorted(self._db.getTelegramGroups())
            if len(tgs) == 0:
                return ["No telegram groups available."]
            else:
                prefix = tgs[0].prefix
                lines = []
                replies = []
                for tg in tgs:
                    if tg.prefix != prefix:
                        replies.append("\n".join(lines))
                        lines = []
                        prefix = tg.prefix
                    lines.append(f"{tg.unitCode} {tg.unitName}")
                    lines.append(tg.link)
                    lines.append("")
                if len(lines) > 0:
                    replies.append("\n".join(lines))
                    lines = []
                return replies
        else:
            try:
                tg = self._db.getTelegramGroup(unitCode)
            except MalformedUnitCodeException:
                return [f"Fail because {unitCode} is a malformed unit code,"]
            except NoTelegramGroupException:
                return [f"Fail because no known telegram group for {unitCode}"]
            else:
                return [f"Click {tg.link} to join {tg.unitCode} {tg.unitName}"]

    def adminlist(self, message:telebot.types.Message) -> List[str]:
        admins = self._db.getAdmins()
        msg = f"The administrator is @{admins[0]}"
        if len(admins) > 1:
            msg = f"The administrators are {', '.join(['@'+ admin for admin in admins])}."
        msg = "Contact an administrator to add or remove a telegram chat group. \n\n" + msg
        return [msg]

    def help(self, message:telebot.types.Message, width=10) -> List[str]:
        commands = [
            "/start",
            "Say hi to the user",
            "",
            "/welcome",
            "Say hi to the user",
            "",
            "/get all",
            "Retrieve all telegram invitation links",
            "",
            "/get [unit code]",
            "Retrieve the telegram invitation link for the unit",
            "",
            "/courseinfo",
            "Request for the course information in pdf format",
            "",
            "/admins",
            "Retrieve the list of administrators",
            "",
            "/help", 
            "Display the commands available to the user",
            "",
        ]
        return ["\n".join(commands)]

class Admin(User):
    def __init__(self, username:str, fullname:str, logger:Logger):
        super().__init__(username, fullname, logger)
        if username not in getDatabase().getAdmins():
            raise NonAdminUserException(username, fullname)

    def help(self, message:telebot.types.Message) -> List[str]:
        commands = [
            "/add [unit code] [link] [unit name]",
            "Add the invitation link for given unit.",
            "",
            "/update [unit code] link [new link]", 
            "Update the invitation link for the given unit.",
            "",
            "/update [unit code] name [new name]", 
            "Update the unit name for the given unit.",
            "",
            "/rm [unit code]", 
            "Remove the invitation link for the given unit.",
            "",
        ]
        return ["\n".join(commands)]
        

    def add(self, message:telebot.types.Message) -> List[str]:
        tokens = message.text.split()
        unitCode = tokens[1].upper()
        link = tokens[2]
        unitName = " ".join(tokens[3:])
        try:
            self._db.addTelegramGroup(unitCode, unitName, link)
        except MalformedUnitCodeException:
            self._logger.error(f"{self._username} added a telegram group with a malformed unit code.")
            return [f"Fail because unit code {unitCode} is malformed."]
        except BadTelegramLinkException:
            self._logger.error(f"{self._username} added a telegram group with a bad telegram link.")
            return [f"Fail because bad telegram link {link} was given for {unitCode}"]
        else:
            return [f"Success. {unitCode} {unitName} added"]

    def update(self, message:telebot.types.Message) -> List[str]:
        tokens = message.text.split()
        if len(tokens) < 4:
            return [f"Fail because the update command has missing arguements."]
        unitCode = tokens[1].upper()
        try:
            tg = self._db.getTelegramGroup(unitCode)
        except MalformedUnitCodeException:
            self._logger.info(f"{self._username} attempted to update {unitCode} with malformed unit code.")
            return [f"Fail because {unitCode} is a malformed unit code."]
        except NoTelegramGroupException:
            self._logger.info(f"{self._username} attempted to  update non-existent Telegram Group for {unitCode}")
            return [f"Fail because no known telegram group for {unitCode}"]
        else:
            mode = tokens[2].upper()
            if mode == "LINK":
                link = tokens[3]
                try:
                    tg.updateLink(link)
                except NoTelegramGroupException:
                    self._logger.info(f"{self._username} attempted to update non-existent Telegram Group for {unitCode}")
                    return [f"Fail because no known telegram group for {unitCode}"]
                except BadTelegramLinkException:
                    self._logger.info(f"{self._username} attempted to update telegram group for {unitCode} with bad link {link}")
                    return [f"Fail because {link} is a bad link."]
                else:
                    self._logger.info(f"{self._username} updated telegram link for {unitCode} with link {link}")
                    return [f"Success. Telegram link for {unitCode} has been updated."]
            elif mode == "NAME":
                name = tokens[3]
                try:
                    tg.updateUnitName(name)
                except NoTelegramGroupException:
                    self._logger.info(f"{self._username} attempted to update non-existent Telegram Group for {unitCode}")
                    return [f"Fail because no known telegram group for {unitCode}"]
                except BadUnitNameException:
                    self._logger.info(f"{self._username} attempted to update telegram group for {unitCode} with bad unit name.")
                    return [f"Fail because bad unit name is provided."]
                else:
                    self._logger.info(f"{self._username} updated unit name for {unitCode} with unit name {name}")
                    return [f"Success. Unit name for {unitCode} has been updated."]
            else:
                self._logger.info(f"{self._username} attempted to update unknown attribute for telegram gorup {unitCode}")
                return [f"Fail because update mode is neither link nor name."]

    def remove(self, message:telebot.types.Message) -> List[str]:
        tokens = message.text.split()
        unitCode = tokens[1].upper()
        try:
            tg = self._db.getTelegramGroup(unitCode)
        except NoTelegramGroupException:
            self._logger.info(f"{self._username} attempted to remove non existent Telegram Group for {unitCode}")
            return [f"Fail because no known Telegram Group for {unitCode}"]
        except MalformedUnitCodeException:
            return [f"Fail because {unitCode} is a malformed unit code."]
        else:
            tg.delete()
            return [f"Success. Telegram group for {unitCode} is deleted."]
