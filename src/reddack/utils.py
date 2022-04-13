# Native imports
import json
import os
from builtins import FileNotFoundError

# 3rd party imports
import jsonpickle

def get_known_items(knownitems_path):
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

def find_latest(message_ts, post_dir):
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

def find_post_requests(moditem, post_dir):
    """Retrieves all POST requests for a given mod item, returns sorted list."""
    recieved_timestamps = []
    requests = []
    for postfile in os.listdir(os.fsencode(post_dir)):
        if (filename := os.fsdecode(postfile)).endswith('.json'):
            request_ts = filename.strip('.json')
            with open(os.path.join(post_dir, filename), 'r') as file:
                request = json.load(file)
            if request['container']['message_ts'] == moditem.message_ts:
                recieved_timestamps.append(request_ts)
                requests.append(request)
            else:
                continue
        else:
            continue
    if len(recieved_timestamps) == 0:
        return ((), ())
    else:
        sortedrequests, sortedtimestamps = zip(*sorted(zip(requests, recieved_timestamps), key=lambda z: z[1]))
        return sortedrequests, sortedtimestamps

def update_knownitems_file(knownitems, path):
    with open(path, 'w+') as itemfile:
        jsonstr = jsonpickle.encode(knownitems)
        print(jsonstr, file=itemfile)

def cleanup_postrequest_json(incomplete_items, path):
    """Remove POST request files for completed items"""
    keepjson_ts = []
    for item in incomplete_items.values():
        requests, timestamps = find_post_requests(item, path)
        if requests:
            for request in requests:
                keepjson_ts.append(request)
    for postfile in os.listdir(os.fsencode(path)):
        if (filename := os.fsdecode(postfile)).strip('.json') not in keepjson_ts:
            os.remove(os.path.join(path, filename))

def cleanup_knownitems_json(incomplete_items, path):
    """Clean known item JSON"""
    with open(path, 'w+') as itemfile:
        jsonstr = jsonpickle.encode(incomplete_items)
        print(jsonstr, file=itemfile)
