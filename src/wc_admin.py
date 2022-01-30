from discord import Message, Member, TextChannel
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import generate_options


def update_watch_channel(channel: TextChannel) -> bool:
    print(channel.name)
    return True


def update_output_channel(channel: TextChannel) -> bool:
    print(channel.name)
    return True

