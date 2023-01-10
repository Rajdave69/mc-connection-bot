import aiohttp
import configparser
import json
import sys
import discord
import logging

import mysql.connector
from discord.ext import commands
from colorlog import ColoredFormatter

intents = discord.Intents.default()


# Initializing the logger
def colorlogger(name: str = 'my-discord-bot') -> logging.log:
    logger = logging.getLogger(name)
    stream = logging.StreamHandler()

    stream.setFormatter(ColoredFormatter("%(reset)s%(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s"))
    logger.addHandler(stream)
    return logger  # Return the logger


log = colorlogger()

# Loading config.ini
config = configparser.ConfigParser()

try:
    config.read('./data/config.ini')
except Exception as e:
    log.critical("Error reading the config.ini file. Error: " + str(e))
    sys.exit()

# Getting variables from config.ini
try:
    # Getting the variables from `[general]`
    log_level: str = config.get('general', 'log_level')
    presence: str = config.get('general', 'presence')
    ptero_panel: str = config.get('general', 'ptero_panel')
    ptero_server_id: str = config.get('general', 'ptero_server_id')

    # Getting the variables from `[secret]`
    discord_token: str = config.get('secret', 'discord_token')
    ptero_apikey: str = config.get('secret', 'ptero_apikey')

    # Getting the variables from `[discord]`
    embed_footer: str = config.get('discord', 'embed_footer')
    embed_color: int = int(config.get('discord', 'embed_color'), base=16)
    embed_url: str = config.get('discord', 'embed_url')

    # get the key-value pairs of `ranks` as a dict
    ranks: dict = dict(config.items('ranks'))

    db_user: str = config.get('secret', 'db_user')
    db_pass: str = config.get('secret', 'db_pass')
    db_host: str = config.get('secret', 'db_host')
    db_name: str = config.get('secret', 'db_name')


except Exception as err:
    log.critical("Error getting variables from the config file. Error: " + str(err))
    sys.exit()

# Set the logger's log level to the one in the config file
if log_level.upper().strip() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    log.setLevel(log_level.upper().strip())
else:
    log.setLevel("INFO")
    log.warning(f"Invalid log level `{log_level.upper().strip()}`. Defaulting to INFO.")

# Initializing the client
client = commands.Bot(intents=intents)  # Setting prefix

_embed_template = discord.Embed(
    title="Success!",
    color=embed_color,
    url=embed_url
)

_embed_template.set_footer(text=embed_footer)

embed_template = lambda: _embed_template.copy()


def error_template(description: str) -> discord.Embed:
    _error_template = discord.Embed(
        description=description,
        color=0xff0000,
        url=embed_url
    )
    _error_template.set_footer(text=embed_footer)

    return _error_template.copy()


def get_con(discord_id) -> str or None:
    con = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_name
    )
    cursor = con.cursor(prepared=True)

    cursor.execute("SELECT username FROM connections WHERE discord_id = ?", (discord_id,))
    data = cursor.fetchone()
    return data[0] if data else None


async def send_cmd(command: str) -> bool:
    url = f'https://{ptero_panel}/api/client/servers/{ptero_server_id}/command'
    headers = {"Authorization": f"Bearer {ptero_apikey}", "Accept": "application/json",
               "Content-Type": "application/json"}
    payload = json.dumps({"command": command})

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as resp:
            response = await resp.json()
    return response['status'] == 'success'

# Add your own functions and variables here
# Happy coding! :D
