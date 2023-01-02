from backend import log, ranks, get_con, send_cmd
from discord.ext import commands


class Listeners(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        self.ranks = ranks

    # Use @command.Cog.listener() for an event-listener (on_message, on_ready, etc.)
    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog: listeners.py Loaded")

    @commands.Cog.listener()  # On role given
    async def on_member_update(self, before, after):

        # If the user is given a role
        if len(before.roles) < len(after.roles):
            new_role = next(
                role for role in after.roles if role not in before.roles)  # Gets the role that the user just got

            if new_role.id in self.ranks.keys():  # If the user just got a Rank Role
                mc_user = await get_con(int(after.id))  # Gets the user's MC account, if exists
                if mc_user is None:  # If the user is not connected
                    return

                role = self.ranks[new_role.id]
                cmd = f"lp user {mc_user} parent add {role}"  # Command to give the user the rank
                await send_cmd(cmd)  # Sends the command to LuckPerms server
                await after.send(
                    f"Greetings, You have been given the `{role}` rank in-game.")
                log.info(f"Gave `{after.name}#{after.discriminator}` the `{role}` rank!")

        # If a role is removed from the user
        if len(before.roles) > len(after.roles):
            removed_role = next(
                role for role in before.roles if role not in after.roles)  # Gets the role that the user just lost
            if removed_role.id in self.ranks.keys():  # If the user just lost a Rank Role
                mc_user = await get_con(int(before.id))  # Gets the user's MC account, if exists
                if mc_user is None:  # If the user is not connected
                    return

                role = self.ranks[removed_role.id]
                cmd = f"lp user {mc_user} parent remove {role}"  # Command to remove the rank
                await send_cmd(cmd)  # Sends the command to LuckPerms server
                await before.send(f"Greetings, The `{role}` "
                                  f"rank has been taken from you in-game.")  # DMs the user on Discord
                log.info(f"Removed `{role}` Role from `{before.name}#{before.discriminator}`")


def setup(client):
    client.add_cog(Listeners(client))
