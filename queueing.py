# Native imports
import json
import os
from builtins import FileNotFoundError

# 3rd party imports
import praw
import jsonpickle

# Local imports
from modfromslack.config import KNOWN_ITEMS, SUBMISSION_CHANNEL, POST_DIR
from modfromslack.types import ModSubmission

def item_is_known(prawitem):
    """Checks if item ID is in JSON file's list of known items"""
    # TODO Detect when message has been sent to Slack queue but not added to
    # the list of known modqueue items
    try:
        with open(KNOWN_ITEMS, 'r') as itemfile:
            jsonstr = f'{itemfile.read()}'
            knownitems = jsonpickle.decode(jsonstr)
    except (json.JSONDecodeError, FileNotFoundError):
        knownitems = {}
    if prawitem.id in knownitems.keys():
        return True, knownitems
    else:
        return False, knownitems

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

def find_requests(moditem):
    """Retrieves all POST requests for a given mod item, returns sorted list."""
    recieved_timestamps = [] # POST request recieved timestamp
    requests = [] # POST request request
    for postfile in os.listdir(os.fsencode(POST_DIR)):
        if (filename := os.fsdecode(postfile)).endswith('.json'):
            request_ts = filename.strip('.json')
            with open(os.path.join(POST_DIR, filename), 'r') as file:
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
        # TODO Consider switching to two lists to enable iterating on null results
        sortedrequests, sortedtimestamps = zip(*sorted(zip(requests, recieved_timestamps), key=lambda z: z[1]))
        return sortedrequests, sortedtimestamps

def process_responses(moditem):
    """Check for responses to mod item message."""
    requests, timestamps = find_requests(moditem)
    if requests:
        for request in requests:
            moderator = request['user']['id']
            if moderator in moditem.responses:
                moditem.responses[moderator].update(request)
            else:
                moditem.initialize_response(moderator)
                moditem.responses[moderator].update(request)

def check_reddit_queue(client, sub, knownitems=None):
    """Check subreddit modqueue for unmoderated items."""
    for item in sub.mod.modqueue(limit=None):
        # Check if item is comment or submission
        if isinstance(item, praw.models.Submission):
            ModItem = ModSubmission
        else:
            print("Ignoring non-submission item.")
            continue
        # Check if item is known
        if knownitems is None:
            isknown, knownitems = item_is_known(item)
        else:
            isknown = True if item.id in knownitems else False
        # Check for responses or send initial message
        if isknown:
            continue
        else:
            moditem = ModItem(item)
            moditem.send_msg(client)
            # Add to known items
            knownitems[item.id] = moditem
            with open(KNOWN_ITEMS, 'w+') as itemfile:
                jsonstr = jsonpickle.encode(knownitems)
                print(jsonstr, file=itemfile)
    return knownitems

def cleanup_json_files(incomplete_items):
    """Remove POST request files for completed items and clean known item JSON"""
    with open(KNOWN_ITEMS, 'w+') as itemfile:
        jsonstr = jsonpickle.encode(incomplete_items)
        print(jsonstr, file=itemfile)
    keepjson_ts = []
    for item in incomplete_items.values():
        requests, timestamps = find_requests(item)
        if requests:
            for request in requests:
                keepjson_ts.append(request)
    for postfile in os.listdir(os.fsencode(POST_DIR)):
        if (filename := os.fsdecode(postfile)).strip('.json') not in keepjson_ts:
            os.remove(os.path.join(POST_DIR, filename))

def check_slack_queue(client, reddit, knownitems):
    """Check Slack items for moderation actions"""
    incomplete = {}
    complete = {}
    if knownitems is None:
        knownitems = {}
    for moditem in knownitems.values():
        process_responses(moditem)
        if moditem.approve_or_remove == "approve":
            reddit.submission(moditem.prawitem).mod.approve()
        elif moditem.approve_or_remove == "remove":
            reddit.submission(moditem.prawitem).mod.remove()
            # TODO Add method for applying removal reasons and sending modmail
        else:
            incomplete[moditem.prawitem] = moditem
            continue
        complete[moditem.prawitem] = moditem
        moditem.complete_cleanup(client)
    cleanup_json_files(incomplete_items=incomplete)
    knownitems = incomplete
    return knownitems
    
