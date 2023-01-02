import os
import sys
from backend import client, discord_token, log, presence
import discord.utils


# This is what gets run when the bot stars
@client.event
async def on_ready():
    log.info(f"Bot is ready. Logged in as {client.user}")
    await client.change_presence(activity=discord.Game(name=presence))


# Loading all .py files in ./cogs as bot cogs.
# If you don't know what a cog is,
# https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html
for file in os.listdir('./cogs'):
    if file.endswith('.py'):
        client.load_extension(f'cogs.{file[:-3]}')


# Run the actual bot
try:
    client.run(discord_token)
except discord.LoginFailure:
    log.critical("Invalid Discord Token. Please check your config file.")
    sys.exit()
except Exception as err:
    log.critical(f"Error while connecting to Discord. Error: {err}")
    sys.exit()