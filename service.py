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
            User(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).welcome(self._telebot, message)

        @self._telebot.message_handler(commands=['get'])
        async def get(message:telebot.types.Message) -> None:
            """
            /get all            return all telegram invitation links
            /get [unitCode]     return telegram invitation link for a specific unit
            """
            await User(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).get(self._telebot, message)

        @self._telebot.message_handler(commands=['admins'])
        async def adminlist( message:telebot.types.Message) -> None:
            """
            /admins             retrieve the list of administrators
            """
            User(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).adminlist(self._telebot, message)
        
        @self._telebot.message_handler(commands=["help"])
        async def help(message:telebot.types.Message) -> None:
            """
            /help               displays all available commands to the user
            """
            try:
                Admin(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).help(self._telebot, message)
            except NonAdminUser:
                User(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).help(self._telebot, message)
            
        @self._telebot.message_handler(commands=["add"])
        async def add(message:telebot.types.Message) -> None:
            """
            /add [unit code] ] [link] [title]       add a telegram group
            """
            try:
                Admin(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).add(self._telebot, message)
            except NonAdminUser:
                self._logger.error(f"Non-admin user {message.from_user.username} attempted to use /add.")
                await self._telebot.reply_to(message, "Fail. You are not authorised to perform /add.")

        @self._telebot.message_handler(commands=["update"])
        async def update(message:telebot.types.Message) -> None:
            """
            /update [unit code] link [new link]         update the telegram link for an academic unit
            /update [unit code] name [new unit name]    update the name of the academic unit
            """
            try:
                Admin(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).update(self._telebot, message)
            except NonAdminUser:
                self._logger.error(f"Non-admin user {message.from_user.username} attempted to use /update.")
                await self._telebot.reply_to(message, "Fail. You are not authorised to perform /update.")

        @self._telebot.message_handler(commands=["rm"])
        async def remove(message:telebot.types.Message) -> None:
            """
            /rm [unitCode]      removes a telegram group for that unit code.
            """
            try:
                Admin(message.from_user.username, message.from_user.full_name, self._admins, self._db, self._logger).remove(self._telebot, message)
            except NonAdminUser:
                self._logger.error(f"Non-admin user {message.from_user.username} attempted to use /rm.")
                await self._telebot.reply_to(message, "Fail. You are not authorised to perform /rm.")

