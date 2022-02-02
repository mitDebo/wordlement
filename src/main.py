import wordlement
import server_cfg

from datetime import datetime, timedelta
import os
import re
from discord import Message, Intents, TextChannel, Guild
from discord.ext import commands
from discord.ext.commands import has_guild_permissions
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

discord_token = os.environ.get("DISCORD_TOKEN")
intents = Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
slash = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print('Ready!')


@slash.slash(
    name="start_tournament",
    description="Starts a new tournament on your server, beginning today and running for num_days",
    guild_ids=[937340367110553691,699613886487461918],
    options=[
        create_option(name="num_days",
                      description="How many days the tournament is. Defaults to 14",
                      option_type=4,
                      required=False
                      )
    ]
)
@has_guild_permissions(administrator=True)
async def _start_tournament(ctx: SlashContext, num_days: int = 14):
    if wordlement.current_tournament(ctx.guild) is not None:
        await ctx.reply("A tournament is already running.")
        return

    end_dt = await wordlement.start_new_tournament(ctx.guild, num_days - 1)
    p_start_dt = datetime.today().strftime("%a, %b %d %Y")
    p_end_dt = end_dt.strftime("%a, %b %d %Y")
    success_message = f"**<@{ctx.author_id}> has started a new Wordlement!**\n" \
                      f"_{p_start_dt} - {p_end_dt}_\n\n" \
                      f"" \
                      f"Submit wordle scores throughout the tournament, and they will be tracked golf style. Hard " \
                      f"mode attempts count for one stroke less. At the end of the tournament, the winner will be " \
                      f"crowned champion until next tournament!"
    await wordlement.out_channel(ctx.guild).send(success_message)
    await ctx.send("Tournament successfully created")


@slash.slash(
    name="out_channel",
    description="Sets the channel the bot outputs to. Defaults to the system channel",
    guild_ids=[937340367110553691,699613886487461918],
    options=[
        create_option(name="channel",
                      description="The channel to set it to",
                      option_type=7,
                      required=False
                      )
    ]
)
@has_guild_permissions(administrator=True)
async def _set_out_channel(ctx: SlashContext, channel: TextChannel):
    wordlement.set_out_channel(ctx.guild, channel)
    await ctx.reply("Done")


@slash.slash(
    name="scorecard",
    description="Prints out your scorecard in the current tournament",
    guild_ids=[937340367110553691,699613886487461918]
)
async def _scorecard(ctx: SlashContext, num_days: int = 14):
    scorecard = get_scorecard_for_player(ctx.guild, ctx.author_id)
    scorecard += scorecard_footer()

    await ctx.reply(f"```{scorecard}```")


@slash.slash(
    name="leaderboard",
    description="Prints out everyone's scorecards. Please do not spam this.",
    guild_ids=[937340367110553691,699613886487461918]
)
async def _scorecard(ctx: SlashContext):
    leaderboard = wordlement.get_leaderboard(ctx.guild)
    scorecard = "```"
    for ld in leaderboard:
        if len(scorecard) > 3:
            scorecard += "\n\n"
        scorecard += get_scorecard_for_player(ctx.guild, ld[0])

    scorecard += scorecard_footer() + "```"

    await ctx.reply(scorecard)


@bot.event
async def on_message(message: Message):
    if message.author.bot:
        return

    if not wordlement.is_correct_channel(message.channel.guild, message.channel):
        return

    current_tournament = wordlement.current_tournament(message.channel.guild)
    if current_tournament is None:
        return

    match = re.match(r"Wordle ([0-9]+) ([1-6|X])/6(\*)?", message.content)
    if match is not None:
        guild_id = int(message.guild.id)
        player = message.author
        wordle_id = int(match.group(1).strip())
        score = match.group(2).strip()
        is_hard_mode = True if match.group(3) is not None else False

        if score == "X":
            score = "7"
        score = int(score)

        wordle_id_for_today = wordlement.wordle_id_for_date(datetime.today())
        if wordle_id != wordle_id_for_today:
            await message.reply(f"Please only submit a score for today's Wordle ({wordle_id_for_today})")
            return
        if wordlement.submit_score(guild_id, player.id, wordle_id, score, is_hard_mode):
            reply = f"{golf_score(score)} Score recorded for <@{message.author.id}> on " \
                      f"{wordle_game(wordle_id, is_hard_mode)}\n"
            scorecard = f"```{get_scorecard_for_player(message.guild, message.author.id)}{scorecard_footer()}```"

            await message.channel.send(reply + scorecard)


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


def wordle_game(worlde_id: int, is_hard: bool) -> str:
    game_str = f"Wordle {worlde_id}"
    if is_hard:
        game_str = game_str + " (Hard Mode)"

    return game_str


def get_scorecard_for_player(guild: Guild, user_id: int) -> str:
    scorecard = wordlement.get_scorecard_for_player(guild, user_id)
    formatted_scorecard = format_wordle_scorecard(scorecard["scorecard"])
    total = scorecard["total"]
    return f"{guild.get_member(user_id).display_name} \n" \
           f"{formatted_scorecard}\n" \
           f"Total: {total}"


def format_wordle_scorecard(scorecard: []) -> str:
    result = ""
    for x in scorecard:
        if x is None:
            result += "| "
        else:
            result = f"{result}|{x}"

    return f"{result}|"


def scorecard_footer():
    return "\n\n*=Hard mode. Counts as n-1 towards score"

bot.run(discord_token)
