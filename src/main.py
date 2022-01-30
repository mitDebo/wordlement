import discord
import os
import wc_admin
from discord import Message, TextChannel
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

from discord_slash.utils.manage_commands import create_option

discord_token = os.environ.get("DISCORD_TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
slash = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print('Ready!')


@slash.slash(
    name="wcadmin",
    description="Wordicomp administration CLI",
    guild_ids=[699613886487461918],
    options=[
        create_option(name="watch_channel",
                      description="Sets the channel the bot watches. If not set, defaults to all channels",
                      required=False,
                      option_type=7),
        create_option(name="output_channel",
                      description="Sets the channel the bot writes results. If not set, defaults to system channel",
                      required=False,
                      option_type=7)
    ]
)
async def _update_admin(ctx: SlashContext,
                        watch_channel: TextChannel = None,
                        output_channel: TextChannel = None):
    member = ctx.author
    if member == bot.user:
        return

    if not member.top_role.permissions.administrator:
        await ctx.send("Permission denied: not an admin")
        return

    if isinstance(watch_channel, TextChannel):
        success = wc_admin.update_watch_channel(watch_channel)
        reply = "Watch channel updated to #" + watch_channel.name if success else "There was an error updating the " \
                                                                                  "watch channel "
        await ctx.send(reply)

    if isinstance(output_channel, TextChannel):
        success = wc_admin.update_output_channel(output_channel)
        reply = "Results channel updated to #" + output_channel.name if success else "There was an error updating the " \
                                                                                     "output channel "
        await ctx.send(reply)


@bot.event
async def on_message(message: Message):
    if message.author == bot.user:
        return


bot.run(discord_token)
