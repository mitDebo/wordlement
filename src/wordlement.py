import functools
import math

import data
import server_cfg

from datetime import datetime, timedelta
from discord import Guild, TextChannel


hard_mode_reduction = 0.25


def set_out_channel(guild: Guild, channel: TextChannel):
    server_cfg.set_out_channel(guild.id, channel.id)


def out_channel(guild: Guild) -> TextChannel:
    cfg = server_cfg.get_server_config(guild.id)
    text_channel_id = cfg['out_channel_id']

    return guild.get_channel(text_channel_id)


def is_correct_channel(guild: Guild, channel: TextChannel):
    return True


def latest_tournament(guild: Guild):
    return data.latest_tournament(guild_id=guild.id)


def is_a_tournament_running(guild: Guild) -> bool:
    latest = latest_tournament(guild)
    return datetime.today() < latest["end_dt"]


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


def get_scorecard_for_player(guild: Guild, user_id: int) -> {}:
    tournament = latest_tournament(guild)
    if tournament is None:
        return None

    scorecard = []
    total = 0
    for x in range(0, len(tournament["days"])):
        day = tournament["days"][x]
        if any(score["user_id"] == user_id for score in day["scores"]):
            score = [x for x in day["scores"] if x["user_id"] == user_id][0]
            raw_score = score["raw_score"]
            if score["is_hard_mode"]:
                scorecard.append((str(raw_score) if raw_score < 7 else "X") + "*")
                total += raw_score - hard_mode_reduction
            else:
                scorecard.append((str(raw_score) if raw_score < 7 else "X"))
                total += raw_score

        else:
            if day["dt"].date() < datetime.today().date():
                scorecard.append('X')
                total += 7
            else:
                scorecard.append(None)

    return {"scorecard": scorecard, "total": math.ceil(total)}


def get_leaderboard(guild: Guild) -> []:
    tournament = latest_tournament(guild)
    totals = {}

    start_dt = tournament["start_dt"]
    end_dt = tournament["end_dt"]
    total_days = (end_dt - start_dt).days

    if datetime.today() < end_dt:
        total_days = max((datetime.today() - start_dt).days, 1)

    for x in range(0, total_days):
        day = tournament["days"][x]
        for score in day["scores"]:
            user_id = score["user_id"]
            raw_score = score["raw_score"]
            is_hard_mode = score["is_hard_mode"]

            if user_id in totals:
                totals[user_id].append(raw_score - hard_mode_reduction if is_hard_mode else raw_score)
            else:
                totals[user_id] = []
                for p in range(0, x):
                    totals[user_id].append(7)
                totals[user_id].append(raw_score - hard_mode_reduction if is_hard_mode else raw_score)

    for k in totals.keys():
        user_scores = totals[k]
        if len(user_scores) < total_days:
            for i in range(0, total_days - len(user_scores)):
                totals[k].append(7)

    totals = sorted(totals.items(), key=functools.cmp_to_key(compare_scores))
    return totals


def compare_scores(item1: (int, list), item2: (int, list)) -> int:
    i1 = item1[1]
    i2 = item2[1]

    sum1 = math.ceil(sum(i1))
    sum2 = math.ceil(sum(i2))

    if sum1 - sum2 != 0:
        return sum1 - sum2
    else:
        if len(i1) == 1 and len(i2) == 1:
            return i1[0] - i2[0]
        else:
            reduced_i1 = i1[int(len(i1) / 2):]
            reduced_i2 = i2[int(len(i2) / 2):]
            return compare_scores((0, reduced_i1), (0, reduced_i2))


def wordle_id_for_date(date: datetime) -> int:
    # Hardcoding values into stuff never breaks; this'll be fine forever
    compare_dt = datetime(year=2022, month=1, day=30)
    jan30_wordle_id = 225
    return jan30_wordle_id + (date - compare_dt).days
