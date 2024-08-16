from typing import List

import shelve
import logging
import asyncio

import telebot
from telebot.async_telebot import AsyncTeleBot

from businesslogic import User, Admin, NonAdminUser

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
            """
            /start      Says hi to user
            /welcome    Says hi to user
            """
            await User(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger, self._telebot).welcome(message)

        @self._telebot.message_handler(commands=['get'])
        async def get(message:telebot.types.Message) -> None:
            """
            /get all            return all telegram invitation links
            /get [unitCode]     return telegram invitation link for a specific unit
            """
            replies = User(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).get(message)
            for reply in replies:
                await self._bot.reply_to(message, reply)

        @self._telebot.message_handler(commands=['admins'])
        async def adminlist( message:telebot.types.Message) -> None:
            """
            /admins             retrieve the list of administrators
            """
            replies = User(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).adminlist(message)
            for reply in replies:
                await self._bot.reply_to(message, reply)
        
        @self._telebot.message_handler(commands=["help"])
        async def help(message:telebot.types.Message) -> None:
            """
            /help               displays all available commands to the user
            """
            try:
                replies = Admin(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).help(message)
            except NonAdminUser:
                replies = await User(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).help(message)
            finally:
                for reply in replies:
                    await self._bot.reply_to(message, reply)

        @self._telebot.message_handler(commands=["add"])
        async def add(message:telebot.types.Message) -> None:
            """
            /add [unit code] ] [link] [title]       add a telegram group
            """
            try:
                replies = Admin(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).add(message)
            except NonAdminUser:
                self._logger.error(f"Non-admin user {message.from_user.username} attempted to use /add.")
                await self._telebot.reply_to(message, "Fail. You are not authorised to perform /add.")
            else:
                for reply in replies:
                    await self._bot.reply_to(message, reply)

        @self._telebot.message_handler(commands=["update"])
        async def update(message:telebot.types.Message) -> None:
            """
            /update [unit code] link [new link]         update the telegram link for an academic unit
            /update [unit code] name [new unit name]    update the name of the academic unit
            """
            try:
                await Admin(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger, self._telebot).update(message)
            except NonAdminUser:
                self._logger.error(f"Non-admin user {message.from_user.username} attempted to use /update.")
                await self._telebot.reply_to(message, "Fail. You are not authorised to perform /update.")

        @self._telebot.message_handler(commands=["rm"])
        async def remove(message:telebot.types.Message) -> None:
            """
            /rm [unitCode]      removes a telegram group for that unit code.
            """
            try:
                replies = Admin(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).remove(message)
            except NonAdminUser:
                self._logger.error(f"Non-admin user {message.from_user.username} attempted to use /rm.")
                await self._telebot.reply_to(message, "Fail. You are not authorised to perform /rm.")
            else:
                for reply in replies:
                    await self._bot.reply_to(message, reply)

