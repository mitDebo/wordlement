import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import os

discord_token = os.environ.get("DISCORD_TOKEN")
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    print('Ready!')


@slash.slash(
    name="hello",
    description="This is just a test command, nothing more."
)
async def _test(ctx: SlashContext):
    await ctx.send(content="Hello World!")


client.run(discord_token)