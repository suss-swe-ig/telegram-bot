from typing import List

import shelve
import logging
import asyncio

import telebot
from telebot.async_telebot import AsyncTeleBot

from businesslogic import User, Admin

class Service:

    def __init__(self, token:str, admins:List[str], logger:logging.Logger, database:shelve.Shelf) -> None:
        self._token = token
        self._admins = admins 
        self._logger = logger
        self._db = database
        self._telebot = AsyncTeleBot(token)
        self._addHandlers()

    def run(self):
        asyncio.run(self._telebot.polling())

    def _addHandlers(self):
        @self._telebot.message_handler(commands=['start','welcome'])
        async def welcome(message:telebot.types.Message) -> None:
            await User(message.from_user.username, self._admins, self._db, self._logger).welcome(self._telebot, message)

        @self._telebot.message_handler(commands=['get'])
        async def get(message:telebot.types.Message) -> None:
            await User(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).get(self._telebot, message)

        @self._telebot. smessage_handler(commands=['admins'])
        async def adminlist(message:telebot.types.Message) -> None:
            await User(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).adminlist(self._telebot, message)
        
        @self._telebot.message_handler(commands=["help"])
        async def help(message:telebot.types.Message) -> None:
            await User(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).help(self._telebot, message)
        
        @self._telebot.message_handler(commands=["add"])
        async def add(message:telebot.types.Message) -> None:
            await Admin(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).add(self._telebot, message)
        
        @self._telebot.message_handler(commands=["update"])
        async def update(message:telebot.types.Message) -> None:
            await Admin(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).update(self._telebot, message)

        @self._telebot.message_handler(commands=["rm"])
        async def remove(message:telebot.types.Message) -> None:
            await Admin(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).remove(self._telebot, message)
