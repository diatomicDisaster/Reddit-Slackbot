import os
import praw
import json
from constants import KNOWN_ITEM_IDS
from payload import build_submission_block
from messaging import newitem_message
from config import submission_channel
from exceptions import MsgSendError

reddit = praw.Reddit(
    client_id=os.environ.get('PRAW_CLIENT_ID'),
    client_secret=os.environ.get('PRAW_CLIENT_SECRET'),
    password=os.environ.get('PRAW_PASSWORD'),
    username=os.environ.get('PRAW_USER'),
    user_agent=os.environ.get('PRAW_AGENT')
)

subreddit = reddit.subreddit(os.environ.get('PRAW_SUBREDDIT'))

class ModItem:
    """Stores information about the state of an item in the modqueue."""
    def __init__(self, prawitem):
        self.prawitem = prawitem
        # self._msg_payload = None
    
    def __getattr__(self, attr):
        return getattr(self.prawitem, attr)

class ModSubmission(ModItem):
    """Stores information about the state of an item in the modqueue."""

    @property
    def msg_payload(self):
        try:
            return build_submission_block(
                self.created_utc, self.mrmen, 
                self.url, self.author.name, 
                self.thumbnail, self.permalink
            )
        except AttributeError as error:
            raise MsgSendError(
                f"{error.obj!r} object is missing field {error.name!r}."
            ) from error 

    # @msg_payload.setter
    # def msg_payload(self):
    #     self._msg_payload = build_submission_block(
    #         self.created_utc, self.title, self.url, self.author.name, 
    #         self.thumbnail, self.permalink
    #     )
    
    # @msg_payload.deleter
    # def msg_payload(self):
    #     del self._msg_payload

def item_is_known(prawitem):
    """Checks if item ID is in list of known IDs"""
    try:
        knownitems = json.loads(KNOWN_ITEM_IDS)
    except json.JSONDecodeError:
        knownitems = []
    if prawitem.id in knownitems:
        return True
    else:
        return False

def process_submission(prawitem):
    """Process submissions in the modqueue."""
    if not item_is_known(prawitem):
        moditem = ModSubmission(prawitem)
        newitem_message(moditem.msg_payload, submission_channel)
        return moditem
    else:
        return None

def check_queue(sub):
    """Check subreddit modqueue for unmoderated items."""
    for item in sub.mod.modqueue(limit=None):
        if isinstance(item, praw.models.Submission):
            process_submission(item)
        else:
            print("Ignoring non-submission item.")