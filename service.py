from typing import List

import shelve
import logging
import asyncio

import telebot
from telebot.async_telebot import AsyncTeleBot

from singleton import Singleton
from businesslogic import User, Admin, NonAdminUserException
from modules import courseinfo

_SERVICE = None

def setup(token:str, logger:logging.Logger):
    global _SERVICE
    _SERVICE = SingletonService(token, logger)

class ServiceNotReadyException(Exception):
    pass

def run():
    global _SERVICE
    if _SERVICE is None:
        raise ServiceNotReadyException()
    _SERVICE.run()
    
class SingletonService(Singleton):

    def __init__(self, token:str, logger:logging.Logger) -> None:
        self._token = token
        self._logger = logger
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
            replies = User(message.from_user.username, message.from_user.full_name, self._logger).welcome(message)
            for reply in replies:
                await self._telebot.reply_to(message, reply)

        @self._telebot.message_handler(commands=['get'])
        async def get(message:telebot.types.Message) -> None:
            """
            /get all            return all telegram invitation links
            /get [unitCode]     return telegram invitation link for a specific unit
            """
            replies = User(message.from_user.username, message.from_user.full_name, self._logger).get(message)
            for reply in replies:
                await self._telebot.reply_to(message, reply)

        @self._telebot.message_handler(commands=['admins'])
        async def adminlist( message:telebot.types.Message) -> None:
            """
            /admins             retrieve the list of administrators
            """
            replies = User(message.from_user.username, message.from_user.full_name, self._logger).adminlist(message)
            for reply in replies:
                await self._telebot.reply_to(message, reply)
        
        @self._telebot.message_handler(commands=["help"])
        async def help(message:telebot.types.Message) -> None:
            """
            /help               displays all available commands to the user
            """
            replies = User(message.from_user.username, message.from_user.full_name, self._logger).help(message)
            for reply in replies:
                await self._telebot.reply_to(message, reply)
            try:
                replies = Admin(message.from_user.username, message.from_user.full_name, self._logger).help(message)
            except NonAdminUserException:
                pass
            else:
                for reply in replies:
                    await self._telebot.reply_to(message, reply)

        @self._telebot.message_handler(commands=["add"])
        async def add(message:telebot.types.Message) -> None:
            """
            /add [unit code] ] [link] [title]       add a telegram group
            """
            try:
                replies = Admin(message.from_user.username, message.from_user.full_name, self._logger).add(message)
            except NonAdminUserException:
                self._logger.error(f"Non-admin user {message.from_user.username} attempted to use /add.")
                await self._telebot.reply_to(message, "Fail. You are not authorised to perform /add.")
            else:
                for reply in replies:
                    await self._telebot.reply_to(message, reply)

        @self._telebot.message_handler(commands=["update"])
        async def update(message:telebot.types.Message) -> None:
            """
            /update [unit code] link [new link]         update the telegram link for an academic unit
            /update [unit code] name [new unit name]    update the name of the academic unit
            """
            try:
                replies = Admin(message.from_user.username, message.from_user.full_name, self._logger).update(message)
            except NonAdminUserException:
                self._logger.error(f"Non-admin user {message.from_user.username} attempted to use /update.")
                await self._telebot.reply_to(message, "Fail. You are not authorised to perform /update.")
            else:
                for reply in replies:
                    await self._telebot.reply_to(message, reply)

        @self._telebot.message_handler(commands=["rm"])
        async def remove(message:telebot.types.Message) -> None:
            """
            /rm [unitCode]      removes a telegram group for that unit code.
            """
            try:
                replies = Admin(message.from_user.username, message.from_user.full_name, self._logger).remove(message)
            except NonAdminUserException:
                self._logger.error(f"Non-admin user {message.from_user.username} attempted to use /rm.")
                await self._telebot.reply_to(message, "Fail. You are not authorised to perform /rm.")
            else:
                for reply in replies:
                    await self._telebot.reply_to(message, reply)

        @self._telebot.message_handler(commands=["courseinfo"])
        async def getcourseinfo(message:telebot.types.Message) -> None:
            cmds = message.json.get('text', '').split(' ')
            courseCode = None
            if len(cmds) > 1:
                courseCode = cmds[1].upper()
            else:
                chatTitle = filter(lambda x: len(x) == 6, message.chat.title.split(' '))
                courseCode = next(chatTitle, None)

            print(f'downloading course info for {courseCode}')
            response = await courseinfo.downloadCourseInfo(courseCode)
            print(f'Response from downloadCourseInfo: {response}')

            pdf = response.get('pdf')
            if pdf is not None:
                chatId = message.chat.id
                messageId = message.message_id
                with open(pdf, 'rb') as file:
                    await self._telebot.send_document(chatId, file, caption="Here's the course information", reply_to_message_id=messageId)
                return

            await self._telebot.reply_to(message, 'I am unable to find the course information.')
