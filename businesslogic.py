from typing import List
from shelve import Shelf
from logging import Logger

import telebot 
from telebot.async_telebot import AsyncTeleBot
import telebot.async_telebot

import persistence

class User:

    def __init__(username:str, fullname:str, admins:List[str], db:Shelf, logger:Logger):
        pass

    async def welcome(self, bot: telebot.async_telebot.AsyncTeleBot, msg:telebot.types.Message) -> None:
        pass

    async def get(self, bot: telebot.async_telebot.AsyncTeleBot, msg:telebot.types.Message) -> None:
        pass

    async def adminlist(self, bot: telebot.async_telebot.AsyncTeleBot, msg:telebot.types.Message) -> None:
        pass

    async def help(self, bot: telebot.async_telebot.AsyncTeleBot, msg:telebot.types.Message) -> None:
        pass

class Admin:

    def __init__(username:str, fullname:str, admins:List[str], db:Shelf, logger:Logger):
        pass

    async def add(self, bot: telebot.async_telebot.AsyncTeleBot, msg:telebot.types.Message) -> None:
        pass

    async def update(self, bot: telebot.async_telebot.AsyncTeleBot, msg:telebot.types.Message) -> None:
        pass

    async def remove(self, bot: telebot.async_telebot.AsyncTeleBot, msg:telebot.types.Message) -> None:
        pass