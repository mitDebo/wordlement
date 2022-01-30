import os
from datetime import date
from pymongo import MongoClient

connection_str = os.environ.get('SQL_CONNECTION_STR')
client = MongoClient(connection_str)
db = client.wordlement


def add_new_score(guild_id:int, user_id:int, wordle_id:int, raw_score:id, is_hard_mode: bool = False) -> bool:
    # we only count your first recorded score
    if __score_exists(guild_id, user_id, wordle_id):
        return False

    score = {
        "guild_id": guild_id,
        "user_id": user_id,
        "wordle_id": wordle_id,
        "raw_score": raw_score,
        "is_hard_mode": is_hard_mode,
        "date": date.today().strftime("%Y-%m-%d")
    }
    db.scores.insert_one(score)
    return True


def __score_exists(guild_id:int, user_id:int, wordle_id:int) -> bool:
    result = db.scores.find_one({
        "guild_id": guild_id,
        "user_id": user_id,
        "wordle_id": wordle_id
    })
    return False if result is None else True
