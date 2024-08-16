from typing import List
from shelve import Shelf
from logging import Logger

import telebot 
from telebot.async_telebot import AsyncTeleBot
import telebot.async_telebot

from persistence import Persistence, TelegramGroup, MalformedUnitCodeException, NoTelegramGroupException

class NonAdminUser(Exception):
    def __init__(self, username, fullname):
        Exception.__init__(self, f"{username} {fullname} is not an administrator")

class User:
    def __init__(self, username:str, fullname:str, admins:List[str], db:Shelf, logger:Logger):
        self._username = username
        self._fullname = fullname
        self._admins = admins
        self._persistence = Persistence(db)
        self._logger = logger
    
    def isAdmin(self) -> bool:
        return self._username in self._admins

    def welcome(self, message:telebot.types.Message) -> List[str]:
        return [f"hello {message.from_user.full_name}. Enter /help to see what commands are available."]

    def get(self, message:telebot.types.Message) -> List[str]:
        tokens = message.text.split()
        unitCode = tokens[1].upper()
        if unitCode == "ALL":
            unitCodes = sorted(self._persistence.getUnitCodes())
            if len(unitCodes) == 0:
                return ["No telegram groups available."]
            else:
                tgs = sorted(self._persistence.getTelegramGroups())
                prefix = tgs[0].prefix
                lines = []
                replies = []
                for tg in tgs:
                    if tg.prefix != prefix:
                        replies.append("\n".join(lines))
                        lines = []
                        prefix = tg.prefix
                    lines.append(f"{tg,unitCode} {tg.unitName}")
                    lines.append(tg.link)
                    lines.append("")
                if len(lines) > 0:
                    replies.append("\n".join(lines))
                    lines = []
                return replies
        else:
            try:
                tg = self._persistence.getTelegramGroup(unitCode)
            except MalformedUnitCodeException:
                return ["Fail because {unitCode} is a malformed unit code,"]
            except NoTelegramGroupException:
                return [f"Fail because no known telegram group for {unitCode}"]
            else:
                return [f"Click {tg.link} to join {tg.unitCode} {tg.unitName}"]

    def adminlist(self, message:telebot.types.Message) -> List[str]:
        msg = f"The administrator is @{self._admins[0]}"
        if len(self._admins) > 1:
            msg = f"The administrators are {", ".join(["@" + admin for admin in self._admins])}."
        msg = "Contact an administrator to add or remove a telegram chat group. \n\n" + msg
        return [msg]

    def help(self, message:telebot.types.Message, width=10) -> List[str]:
        commands = [
            f"{'command'.center(width)} {'description'.center(width)}",
            f"{'='*width} {'='*width}",
            f"{'/start'.ljust(width)} Say hi to the user",
            f"{'/welcome'.ljust(width)} Say hi to the user",
            f"{'/get all'.ljust(width)}	Retrieve all telegram invitation links",
            f"{'/get [unit code]'.ljust(width)} Retrieve the telegram invitation link for the unit",
            f"{'/admins'.ljust(width)} Retrieve the list of administrators",
            f"{'/help'.ljust(width)} Display the commands available to the user",
        ]
        return ["\n".join(commands)]

class Admin(User):
    def __init__(self, username:str, fullname:str, admins:List[str], db:Shelf, logger:Logger, bot: AsyncTeleBot):
        if username not in admins:
            raise NonAdminUser(username, fullname)
        User.__init__(self, username, fullname, admins, db, logger, bot)

    def help(self, message:telebot.types.Message) -> None:
        width = 40
        replies = User.help(self, message, width)
        commands = [
            f"{'/add [unit code] [link] [unit name]'.ljust(width)} Add the invitation link for given unit.",
            f"{'/update [unit code] link [new link]'.ljust(width)} Update the invitation link for the given unit.",
            f"{'/update [unit code] name [new name]'.ljust(width)} Update the unit name for the given unit.",
            f"{'/rm [unit code]'.ljust(width)} Remove the invitation link for the given unit.",
        ]
        replies.append("\n".join(commands))
        return replies

    def add(self, msg:telebot.types.Message) -> List[str]:
        pass

    def update(self, msg:telebot.types.Message) -> List[str]:
        pass

    def remove(self, msg:telebot.types.Message) -> List[str]:
        pass