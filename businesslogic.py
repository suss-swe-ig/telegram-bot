from typing import List
from shelve import Shelf
from logging import Logger

import telebot 
from telebot.async_telebot import AsyncTeleBot
import telebot.async_telebot

class NonAdminUser(Exception):
    def __init__(self, username, fullname):
        Exception.__init__(self, f"{username} {fullname} is not an administrator")

class User:

    def __init__(self, username:str, fullname:str, admins:List[str], db:Shelf, logger:Logger, bot:t AsyncTeleBot):
        self._username = username
        self._fullname = fullname
        self._admins = admins
        self._db = db
        self._logger = logger
        self._bot = bot

    async def welcome(self, bot: telebot.async_telebot.AsyncTeleBot, msg:telebot.types.Message) -> None:
        pass

    async def get(self, msg:telebot.types.Message) -> None:
        pass

    async def adminlist(self, msg:telebot.types.Message) -> None:
        pass

    async def help(self, msg:telebot.types.Message) -> None:
        pass

class Admin(User):

    def __init__(self, username:str, fullname:str, admins:List[str], db:Shelf, logger:Logger, bot: AsyncTeleBot):
        if username not in admins:
            raise NonAdminUser(username, fullname)
        User.__init__(self, username, fullname, admins, db, logger, bot)

    async def help(self, msg:telebot.types.Message) -> None:
        pass

    async def add(self, msg:telebot.types.Message) -> None:
        pass

    async def update(self, msg:telebot.types.Message) -> None:
        pass

    async def remove(self, msg:telebot.types.Message) -> None:
        pass