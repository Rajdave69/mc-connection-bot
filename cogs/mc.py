import discord
import mysql.connector
import mysql.connector
import random
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

        self.cur.execute("SELECT discord_id FROM `connection` WHERE code = %s", (code,))
        id_result = self.cur.fetchone()

        if not id_result:
            await ctx.followup.send(error_template("The code is invalid. Did you go in-game and type `/connect`?"))
            return

        if int(id_result[0]) != 0:  # If the code is already used
            await ctx.followup.send(error_template("The Minecraft account is already connected to a Discord account."))
            return

        self.cur.execute("UPDATE `connection` SET `discord_id` = %s WHERE `code` = %s", (ctx.author.id, code))
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

        self.cur.execute("SELECT username FROM `connection` WHERE `discord_id` = ?", (ctx.author.id,))
        id_result = self.cur.fetchone()

        if not id_result:
            await ctx.followup.send(error_template("You are not connected to a Minecraft account."))
            return

        self.cur.execute("DELETE FROM `connection` WHERE `discord_id` = ?", (ctx.author.id,))
        self.con.commit()

        embed = embed_template()
        embed.add_field(name="Success", value="Your Discord account is now disconnected from your Minecraft account.")
        await ctx.followup.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(
        name="forceconnect",
        description="Force connects a Discord account to a Minecraft Account",
    )
    async def forcecon(self, ctx, discord_id: int, uuid: str):
        await ctx.defer()

        self.cur.execute("SELECT `discord_id` FROM `connection` WHERE code = %s", (uuid,))
        id_result = self.cur.fetchone()

        if id_result:
            self.cur.execute("UPDATE `connection` SET `discord_id` = %s WHERE `code` = %s", (discord_id, uuid))

        else:
            self.cur.execute("INSERT INTO `connection` (`discord_id`, `code`, `username`) VALUES (?, ?, ?)",
                             (discord_id, random.randint(100000, 999999), uuid))

        self.con.commit()
        embed = embed_template()
        embed.title = "Success"
        embed.add_field(name="Success", value="The Discord account is now connected to the Minecraft account.")
        await ctx.followup.send(embed=embed)


def setup(client):
    client.add_cog(MC(client))
