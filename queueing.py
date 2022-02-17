import os
import praw
import json
from constants import KNOWN_ITEM_IDS
from payload import build_submission_blocks
from messaging import newitem_message
from config import SUBMISSION_CHANNEL
from exceptions import MsgSendError


class ModItem:
    """Stores information about the state of an item in the modqueue."""
    def __init__(self, prawitem):
        self.prawitem = prawitem
    
    def __getattr__(self, attr):
        return getattr(self.prawitem, attr)

    def send_msg(self):
        ts = newitem_message(self.msg_payload, self.slackchannel)
        self.message_ts = ts

class ModSubmission(ModItem):
    """Stores information about the state of an item in the modqueue."""
    
    slackchannel = SUBMISSION_CHANNEL
    
    def __init__(self, prawitem):
        self.prawitem = prawitem
        self.message_ts = None

    @property
    def msg_payload(self):
        try:
            return build_submission_blocks(
                self.created_utc, self.title, 
                self.url, self.author.name, 
                self.thumbnail, self.permalink
            )
        except AttributeError as error:
            raise MsgSendError(
                f"{error.obj!r} object is missing field {error.name!r}."
            ) from error

def item_is_known(prawitem):
    """Checks if item ID is in list of known IDs"""
    try:
        with open(KNOWN_ITEM_IDS, 'r+') as idfile:
            knownitems = json.load(idfile)
    except json.JSONDecodeError:
        knownitems = []
    if prawitem.id in knownitems:
        return True, knownitems
    else:
        return False, knownitems

def process_moditem(prawitem):
    """Process item in the modqueue."""
    isknown, knownitems = item_is_known(prawitem)
    if isknown:
        return None
    else:
        if isinstance(prawitem, praw.models.Submission):
            moditem = ModSubmission(prawitem)
        else:
            print("Ignoring non-submission item.")
            return
        moditem.send_msg()
        knownitems.append(prawitem.id)
        with open(KNOWN_ITEM_IDS, 'w+') as idfile:
            json.dump(knownitems, idfile)
        return

def check_queue(sub):
    """Check subreddit modqueue for unmoderated items."""
    for item in sub.mod.modqueue(limit=None):
        try:
            process_moditem(item)
        except:
            continue

# Development code
reddit = praw.Reddit(
    client_id=os.environ.get('PRAW_CLIENT_ID'),
    client_secret=os.environ.get('PRAW_CLIENT_SECRET'),
    password=os.environ.get('PRAW_PASSWORD'),
    username=os.environ.get('PRAW_USER'),
    user_agent=os.environ.get('PRAW_AGENT')
)

subreddit = reddit.subreddit(os.environ.get('PRAW_SUBREDDIT'))

check_queue(subreddit)