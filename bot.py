from typing import List, Tuple

import telebot
import shelve
import logging

TOKEN = ""
ADMINS = []
BOT = None
LOGGER = None
DB = "database.db"

def getBot(token:str, admins:List[str], logger:logging.Logger) -> telebot.TeleBot:
    global TOKEN, ADMINS, LOGGER, BOT
    TOKEN = token 
    ADMINS = admins
    LOGGER = logger
    BOT = telebot.TeleBot(token)
    return BOT

    
