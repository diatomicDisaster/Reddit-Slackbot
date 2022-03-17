# Native imports
import json
import os
from builtins import FileNotFoundError

# 3rd party imports
import praw
import jsonpickle

# Local imports 
from reddack.core import (
    Reddack, 
    ReddackSubmission
)

def known_items(knownitems_path):
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

def find_latest(message_ts):
    """Retrieves the latest POST request timestamp for a given message."""
    latest_ts = message_ts
    for postfile in os.listdir(os.fsencode(POST_DIR)):
        if (filename := os.fsdecode(postfile)).endswith('.json'):
            request_ts = filename.strip('.json')
            if request_ts < latest_ts: 
                continue
            else:
                with open(os.path.join(POST_DIR, filename), 'r') as file:
                    request = json.load(file)
                if request['container']['message_ts'] == message_ts:
                    if request_ts > latest_ts : latest_ts = request_ts
                else:
                    continue
        else:
            continue
    return latest_ts

def find_requests(moditem, post_dir):
    """Retrieves all POST requests for a given mod item, returns sorted list."""
    recieved_timestamps = [] # POST request recieved timestamp
    requests = [] # POST request request
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

def process_responses(moditem, post_dir):
    """Check for responses to mod item message."""
    requests, timestamps = find_requests(moditem, post_dir)
    if requests:
        for request in requests:
            moderator = request['user']['id']
            if moderator in moditem.responses:
                moditem.responses[moderator].update(request)
            else:
                moditem.initialize_response(moderator)
                moditem.responses[moderator].update(request)

def check_reddit_queue(reddack: Reddack, knownitems):
    """Check subreddit modqueue for unmoderated items."""
    newitems = {}
    for item in reddack.subreddit.mod.modqueue(limit=None):
        # Check if item is comment or submission
        if isinstance(item, praw.models.Submission):
            ReddackItem = ReddackSubmission
        else:
            print("Ignoring non-submission item.")
            continue
        # Check if item is known
        isknown = True if item.id in knownitems else False
        if isknown:
            continue
        else:
            newitems[item.id] = ReddackItem(item)
    return newitems

def update_slack_queue(reddack: Reddack, newitems, knownitems):
    for id, moditem in newitems.items():
        moditem.send_msg(
            reddack.slack_client, 
            reddack.channels[type(moditem)]['queue']
        )
        # Add to known items
        knownitems[id] = moditem
    return knownitems

def update_knownitems(knownitems, path):
    with open(path, 'w+') as itemfile:
        jsonstr = jsonpickle.encode(knownitems)
        print(jsonstr, file=itemfile)

def cleanup_postrequest_json(incomplete_items, path):
    """Remove POST request files for completed items"""
    keepjson_ts = []
    for item in incomplete_items.values():
        requests, timestamps = find_requests(item)
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

def check_slack_queue(reddack: Reddack, knownitems):
    """Check Slack items for moderation actions"""
    incomplete = {}
    complete = {}
    if knownitems is None:
        knownitems = {}
    for moditem in knownitems.values():
        kind = type(moditem)
        process_responses(moditem, reddack.post_requests_path)
        if moditem.approve_or_remove(reddack.thresholds[kind]) == "approve":
            reddack.praw_client.submission(moditem.prawitem).mod.approve()
        elif moditem.approve_or_remove(reddack.thresholds[kind]) == "remove":
            reddack.praw_client.submission(moditem.prawitem).mod.remove()
            # TODO Add method for applying removal reasons and sending modmail
        else:
            incomplete[moditem.prawitem] = moditem
            continue
        complete[moditem.prawitem] = moditem
        moditem.complete_cleanup(
            reddack.slack_client, 
            reddack.slack_user_client, 
            reddack.channels[kind]
        )
    cleanup_knownitems_json(incomplete, reddack.known_items_path)
    cleanup_postrequest_json(incomplete, reddack.post_requests_path)
    knownitems = incomplete
    return knownitems
    
