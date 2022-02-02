import os
from pymongo import MongoClient

connection_str = os.environ.get('SQL_CONNECTION_STR')
client = MongoClient(connection_str)
db = client.wordlement


def get_server_config(guild_id: int) -> {}:
    cfg = db.server_cfgs.find_one({"guild_id": guild_id})
    if cfg is None:
        cfg = create_new_server_cfg(guild_id)

    return cfg


def create_new_server_cfg(guild_id: int) -> {}:
    new_cfg = {"guild_id": guild_id}
    db.server_cfgs.insert_one(new_cfg)
    return new_cfg


def set_out_channel(guild_id: int, channel_id: int):
    if get_server_config(guild_id) is None:
        create_new_server_cfg(guild_id)

    db.server_cfgs.update_one(
        {"guild_id": guild_id},
        {"$set": {"out_channel_id": channel_id}}
    )
