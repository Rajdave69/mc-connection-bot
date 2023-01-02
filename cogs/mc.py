#   ╔═╗╔═╗            ╔╗       ╔╗ ╔╗     ╔══╗      ╔╗              ╔═══╗╔═══╗╔═══╗
#   ║║╚╝║║            ║║       ║║ ║║     ║╔╗║     ╔╝╚╗             ║╔═╗║║╔═╗║║╔═╗║
#   ║╔╗╔╗║╔══╗╔══╗╔═╗ ║╚═╗╔══╗ ║║ ║║     ║╚╝╚╗╔══╗╚╗╔╝             ║║ ╚╝║║ ║║║║ ╚╝
#   ║║║║║║║╔╗║║╔╗║║╔╗╗║╔╗║╚ ╗║ ║║ ║║     ║╔═╗║║╔╗║ ║║     ╔═══╗    ║║ ╔╗║║ ║║║║╔═╗
#   ║║║║║║║╚╝║║╚╝║║║║║║╚╝║║╚╝╚╗║╚╗║╚╗    ║╚═╝║║╚╝║ ║╚╗    ╚═══╝    ║╚═╝║║╚═╝║║╚╩═║
#   ╚╝╚╝╚╝╚══╝╚══╝╚╝╚╝╚══╝╚═══╝╚═╝╚═╝    ╚═══╝╚══╝ ╚═╝             ╚═══╝╚═══╝╚═══╝
#
#
#   This is a cog belonging to the Moonball Bot.
#   We are Open Source => https://moonball.io/opensource
#
#   This code is not intended to be edited but feel free to do so
#   More info can be found on the GitHub page:
#

import discord
import mysql.connector
import mysql.connector
import sqlite3
from discord.commands import SlashCommandGroup
from discord.ext import commands

from backend import embed_template, error_template, db_host, db_name, db_user, db_pass  # Import bot variables
from backend import log

mc = discord.SlashCommandGroup("mc", "Minecraft Related Commands")


class MC(commands.Cog):
    """Commands interacting with the Minecraft server, meant for the general user."""

    def __init__(self, client):
        self.client = client

        try:
            self.con = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_pass,
                database=db_name
            )
            self.cur = self.con.cursor(prepared=True)
        except Exception as e:
            log.critical(f"[MC]: Error while connecting to database. Error: {str(e)}")
            exit(2)

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: MC.py Loaded")

    @commands.slash_command(
        name="connect",
        description="Connects your Discord account to your Minecraft Account",
    )
    async def con(self, ctx, code: str):
        await ctx.defer()

        self.cur.execute("SELECT discord FROM `connection` WHERE `code` = %s", (code,))
        id_result = self.cur.fetchone()

        if not id_result:
            await ctx.followup.send(error_template("The code is invalid. Did you go in-game and type `/connect`?"))
            return

        if int(id_result[0]) != 0:  # If the code is already used
            await ctx.followup.send(error_template("The Minecraft account is already connected to a Discord account."))
            return

        self.cur.execute("UPDATE `connection` SET `discord_id` = %s, WHERE `code` = %s", (ctx.author.id, code))
        self.con.commit()

        # Insert into the database
        embed = embed_template()
        embed.add_field(name="Success", value="Your Discord account is now connected to your Minecraft account.")
        await ctx.followup.send(embed=embed)

    @commands.slash_command(
        name="disconnect",
        description="Disconnects your Discord account from your Minecraft Account",
    )
    async def discon(self, ctx):
        await ctx.defer()

        self.cur.execute("SELECT uuid FROM `connection` WHERE `discord_id` = ?", (ctx.author.id,))
        id_result = self.cur.fetchone()

        if not id_result:
            await ctx.followup.send(error_template("You are not connected to a Minecraft account."))
            return

        self.cur.execute("DELETE FROM `connection` WHERE `discord_id` = ?", (ctx.author.id,))
        self.con.commit()

        embed = embed_template()
        embed.add_field(name="Success", value="Your Discord account is now disconnected from your Minecraft account.")
        await ctx.followup.send(embed=embed)


def setup(client):
    client.add_cog(MC(client))
