# Native imports
import json
import os
from builtins import FileNotFoundError
from pathlib import Path

# 3rd party imports
import jsonpickle

def get_known_items(knownitems_path: Path) -> dict:
    """Checks if item ID is in JSON file's list of known items"""
    # TODO Detect when message has been sent to Slack queue but not added to
    # the list of known modqueue items
    try:
        with open(knownitems_path, 'r') as itemfile:
            jsonstr = f'{itemfile.read()}'
            knownitems = jsonpickle.decode(jsonstr)
    except (json.JSONDecodeError, FileNotFoundError):
        knownitems = {}
    return knownitems

def find_latest(message_ts: str, post_dir: Path) -> str:
    """Retrieves the latest POST request timestamp for a given message."""
    latest_ts = message_ts
    for postfile in os.listdir(os.fsencode(post_dir)):
        if (filename := os.fsdecode(postfile)).endswith('.json'):
            request_ts = filename.strip('.json')
            if request_ts < latest_ts: 
                continue
            else:
                with open(os.path.join(post_dir, filename), 'r') as file:
                    request = json.load(file)
                if request['container']['message_ts'] == message_ts:
                    if request_ts > latest_ts : latest_ts = request_ts
                else:
                    continue
        else:
            continue
    return latest_ts

def update_knownitems_file(knownitems: dict, knownitems_path: Path):
    with open(knownitems_path, 'w+') as itemfile:
        jsonstr = jsonpickle.encode(knownitems)
        print(jsonstr, file=itemfile)

def clean_post_request(incomplete_items: dict, postrequest_path: Path):
    """Remove POST request files for completed items"""
    keepjson_ts = []
    for item in incomplete_items.values():
        requests, timestamps = item.find_post_requests(postrequest_path)
        if requests:
            for request in requests:
                keepjson_ts.append(request)
    for postfile in postrequest_path.iterdir():
        if postfile.stem not in keepjson_ts:
            os.remove(postfile)

def cleanup_knownitems_json(incomplete_items: dict, knownitems_path: Path):
    """Clean known item JSON"""
    with open(knownitems_path, 'w+') as itemfile:
        jsonstr = jsonpickle.encode(incomplete_items)
        print(jsonstr, file=itemfile)
