from typing import List, Tuple

import telebot
import shelve
import logging
import asyncio

import telebot.async_telebot

TOKEN = ""
ADMINS = []
BOT: telebot.asynctelebot.AsyncTeleBot = None
LOGGER = None
DB = "database.db"

def setupBot(token:str, admins:List[str], logger:logging.Logger) -> None:
    global TOKEN, ADMINS, LOGGER
    TOKEN = token 
    ADMINS = admins
    LOGGER = logger
    BOT = telebot.asynctelebot.AsyncTeleBot(token)

def startPolling() -> None:
    global BOT
    if BOT is not None:
        asyncio.run(BOT.polling())


    
