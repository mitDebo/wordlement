import datetime
import os
import wordlement
from datetime import datetime, timedelta
from pymongo import MongoClient

connection_str = os.environ.get('SQL_CONNECTION_STR')
client = MongoClient(connection_str)
db = client.wordlement


def add_new_tournament(guild_id: int, start_dt: datetime, end_dt: datetime):
    days = []

    for x in range((end_dt-start_dt).days + 1):
        dt = start_dt + timedelta(days=x)
        days.append({
            "dt": dt,
            "wordle_id": wordlement.wordle_id_for_date(dt),
            "scores": []
        })
    tournament = {
        "guild_id": guild_id,
        "start_dt": start_dt,
        "end_dt": end_dt,
        "days": days
    }
    db.tournaments.insert_one(tournament)


def add_new_score(guild_id: int, user_id: int, wordle_id: int, raw_score: id, is_hard_mode: bool = False) -> bool:
    # we only count your first recorded score
    if __score_exists(guild_id, user_id, wordle_id):
        return False

    score = {
        "user_id": user_id,
        "raw_score": raw_score,
        "is_hard_mode": is_hard_mode
    }
    db.tournaments.update_one(
        {
            "guild_id": guild_id,
            "start_dt": {"$lte": datetime.today()},
            "end_dt": {"$gte": datetime.today()},
            "days.wordle_id": wordle_id
        },
        {
            "$addToSet": {"days.$.scores": score}
        }
    )
    return True


def current_tournament(guild_id:int) -> {}:
    today = datetime.today()
    tournament = db.tournaments.find({
        "guild_id": guild_id,
        "start_dt": {"$lte": today},
        "end_dt": {"$gte": today}
    })

    for t in tournament:
        return t

    return None


def __score_exists(guild_id:int, user_id:int, wordle_id:int) -> bool:
    result = db.tournaments.find_one({
        "guild_id": guild_id,
        "days.$.scores.user_id": user_id,
        "days.wordle_id": wordle_id
    },)
    return False if result is None else True
