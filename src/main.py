import discord
from discord import Message, Member
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import os

discord_token = os.environ.get("DISCORD_TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print('Ready!')


@bot.event
async def on_message(message:Message):
    if message.author == bot.user:
        return

    if is_josh(message.author):
        message.reply("Fuck you, Josh")


@slash.slash(
    name="hello",
    description="This is just a test command, nothing more."
)
async def _test(ctx: SlashContext):
    await ctx.send(content="Hello World!")


def is_josh(member: Member) -> bool:
    josh_id = 273219725587382272  # josh's discord id that I looked up
    return member.id == josh_id


bot.run(discord_token)