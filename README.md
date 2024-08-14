# SUSS Telegram Groups Bot

The telegram handler for this bot is @SUSS_Telegram_Groups_Bot

You may query this bot to retrieve the telegram invitation link for your unit

## Configuration

create a .env file in the root directory of the project with the following content:

> TOKEN=[Telegram API Token]  
> ADMINS=admin1,admin2  
> DATABASE=[file name for database]  

TOKEN is the Telegram API Token.  

ADMINS is a list of Telegram usernames (seperated by commas) who are allowed to perform administrative actions on the bot.  

DATABASE is the filename of the persistence database which contains the telegram invitation links.

## How to use the bot?

