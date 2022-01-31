import data

from datetime import datetime, timedelta
from discord import Guild, TextChannel


def out_channel(guild: Guild) -> TextChannel:
    return guild.system_channel


def watch_channel(guild: Guild) -> TextChannel:
    return None


def is_correct_channel(guild:Guild, channel:TextChannel):
    return True


def current_tournament(guild: Guild):
    return data.current_tournament(guild_id=guild.id)


async def start_new_tournament(guild: Guild, num_days: int) -> datetime:
    today = datetime(year=datetime.today().year,
                     month=datetime.today().month,
                     day=datetime.today().day)

    end_dt = today + timedelta(days=num_days)
    data.add_new_tournament(guild_id=guild.id, start_dt=today, end_dt=end_dt)
    return end_dt


def submit_score(guild_id: int,
                 player_id: int,
                 wordle_id: int,
                 score: int,
                 is_hard_mode: bool) -> bool:
    return data.add_new_score(guild_id, player_id, wordle_id, score, is_hard_mode)


def wordle_id_for_date(date: datetime) -> int:
    # Hardcoding values into stuff never breaks; this'll be fine forever
    compare_dt = datetime(year=2022, month=1, day=30)
    jan30_wordle_id = 225
    return jan30_wordle_id + (date - compare_dt).days
