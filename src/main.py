import os
import re
from discord import Message, Intents
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

discord_token = os.environ.get("DISCORD_TOKEN")
intents = Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
slash = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print('Ready!')


@slash.slash(
    name="hello",
    description="hello",
    guild_ids=[937340367110553691]
)
async def _hello_world(ctx: SlashContext):
    await ctx.send("Hello, world")


@bot.event
async def on_message(message: Message):
    if message.author.bot:
        return

    match = re.match(r"Wordle ([0-9]+) ([1-6|X])/6(\*)?", message.content)
    if match is not None:
        player = message.author
        wordle_id = match.group(1).strip()
        score = match.group(2).strip()
        is_hard = True if match.group(3) is not None else False

        if score == "X":
            score = "7"
        score = int(score)

        await message.channel.send(f"{golf_score(score)} Score recorded for <@{message.author.id}>"
                                   f"on {wordle_game(wordle_id, is_hard)}")


def golf_score(score: int) -> str:
    if score == 1:
        return "HOLE IN ONE!!"
    if score == 2:
        return "Eagle!"
    if score == 3:
        return "Birdie!"
    if score == 4:
        return "Par."
    if score == 5:
        return "Bogey."
    if score == 6:
        return "Double Bogey."
    if score == 7:
        return "Womp womp..."


def wordle_game(id: str, is_hard: bool) -> str:
    game_str = f"Wordle {id}"
    if is_hard:
        game_str = game_str + " (Hard Mode)"

    return game_str



bot.run(discord_token)
