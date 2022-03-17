from __future__ import annotations
import abc
from ast import Mod
import os
from typing import (
    Type,
    Union,
    TypedDict
)
from pathlib import Path

# 3rd party imports
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from praw import Reddit
import jsonpickle

# Local imports
from reddack.payload import (
    build_submission_blocks, 
    build_response_block, 
    build_archive_blocks
)
from reddack.exceptions import (
    MsgSendError, 
    ActionSequenceError
)
from reddack.slack import (
    Confirm,
    ApproveRemove,
    RemovalReason,
    Modnote,
    Action
)

# TODO Add functionality for flairing posts
# TODO Add functionality for awarding posts

class SubmissionResponse:
    """Class for storing moderator responses to Slack mod item messages."""
    def __init__(self, parentmsg_ts):
        self.parentmsg_ts = parentmsg_ts
        self.actions = {
            'actionConfirm' : Confirm(),
            'actionSeePost' : Action()
            }
        self.states = {
            'actionApproveRemove' : ApproveRemove(),
            'actionRemovalReason' : RemovalReason(),
            'actionModnote' : Modnote()
            }

    def update(self, request):
        """Update response with actions from Slack payload."""
        for action in request['actions']:
            if action['action_id'] in self.actions:
                if action['action_ts'] < self.parentmsg_ts:
                    raise ActionSequenceError(
                        "parent message", 
                        "action",
                        afterword="Something went wrong when updating responses, "
                        "if app has rebooted, try clearing known item JSON file."
                        )
                self.actions[action['action_id']].update(action)
        for blockid, blockvalue in request['state']['values'].items():
            for state in self.states:
                if state in blockvalue:
                    self.states[state].update(blockvalue[state])


class ReddackItem:
    """Stores information about the state of an item in the modqueue."""
    def __init__(self, prawitem):
        self.prawitem = prawitem.id
        self.message_ts = None
        self.responses = {}

class ReddackComment(ReddackItem):
    """Stores information about the state of a comment in the modqueue."""

class ReddackSubmission(ReddackItem):
    """Stores information about the state of a submission in the modqueue."""

    _ResponseType : Type = SubmissionResponse

    def __init__(self, prawitem):
        self.created_utc = prawitem.created_utc 
        self.title = prawitem.title
        self.url = prawitem.url
        self.author = prawitem.author.name
        self.thumbnail = prawitem.thumbnail
        self.text = prawitem.selftext
        self.permalink = prawitem.permalink
        super().__init__(prawitem)

    def send_msg(self, client, channel):
        """Send message for new mod item to specified Slack channel"""
        # TODO Handle missing thumbnail URL gracefully, as many third party 
        # sources do not appear to permalink thumbnails.
        try:
            result = client.chat_postMessage(
                blocks=self.msg_payload, channel=channel, 
                text="New modqueue item", unfurl_links=False, unfurl_media=False
            )
            result.validate()
            self.message_ts = result.data['ts']
            return result
        except SlackApiError as error:
            raise MsgSendError("Failed to send item to Slack.") from error

    def _delete_msg(self, client, user_client, channel):
        """Delete replies to mod item message"""
        response = client.conversations_replies(
            channel=channel, 
            ts=self.message_ts
        )
        for message in response["messages"][::-1]:
            reply_response = user_client.chat_delete(
                channel=channel, 
                ts=message["ts"],
                as_user=True
            )

    def _send_archive(self, client, channel):
        """Send archive message after mod actions are complete"""
        responseblocks = []
        for userid, modresponse in self.responses.items():
            response = client.users_info(user=userid)
            name = response["user"]["real_name"]
            responseblocks.append(
                build_response_block(
                    name, 
                    modresponse.states["actionApproveRemove"].value, 
                    modresponse.states["actionRemovalReason"].value
                )
            )
        archiveblocks = build_archive_blocks(
            self.created_utc, 
            self.title,
            self.author,
            self.permalink,
            responseblocks,
        )
        with open("debugdump.json", "w+") as f:
            blocksjson = jsonpickle.encode(archiveblocks)
            print(blocksjson, file=f)
        result = client.chat_postMessage(
            blocks=archiveblocks, channel=channel,
            text="Archived modqueue item", unfurl_links=False, unfurl_media=False
        )

    def complete_cleanup(self, client, user_client, channels):
        """Delete message and send to archive after completion"""
        self._send_archive(client, channels['archive'])
        self._delete_msg(client, user_client, channels['queue'])

    def initialize_response(self, moderator):
        """Initialize a new moderator response object"""
        self.responses[moderator] = self._ResponseType(self.message_ts)
    
    def approve_or_remove(self, thresholds):
        votesum = 0
        for response in self.responses.values():
            if response.actions['actionConfirm'].value: 
                votesum += float(response.states['actionApproveRemove'].value)
        if votesum >= thresholds['approve']:
            return 'approve'
        elif votesum <= thresholds['remove']:
            return "remove"
        else:
            return None
    
    @property
    def msg_payload(self):
        try:
            return build_submission_blocks(
                self.created_utc, 
                self.title, 
                self.url, 
                self.author, 
                self.thumbnail,
                self.text,
                self.permalink
            )
        except AttributeError as error:
            raise MsgSendError(
                f"{error.obj!r} object is missing field {error.name!r}."
            )

    @property
    def removal_reasons(self):
        unique_reasons = []
        for response in self.responses:
            for reason in response.states['actionRemovalReason'].value:
                if reason not in unique_reasons: unique_reasons.append(reason)
        return sorted(unique_reasons)


class Auth(abc.ABC):
    @abc.abstractmethod
    def create_client(self):
        pass

class PrawAuth(Auth):

    AGENT = "r/SpaceX Slack moderation interface by u/ModeHopper"

    def __init__(self, client_id, client_secret, username, password):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password

    def create_client(self):
        return Reddit(
            client_id = self.client_id,
            client_secret = self.client_secret,
            password = self.password,
            username = self.username,
            user_agent = self.AGENT
        )

class SlackAuth(Auth):
    def __init__(self, bot_token, user_token):
        self.bot_token = bot_token
        self.user_token = user_token

    def create_client(self, as_user=False):
        return WebClient(token=(self.user_token if as_user else self.bot_token))

class Thresholds(TypedDict):
    approve: int
    remove: int

class Channels(TypedDict):
    queue: str
    archive: str

class RemovalTemplate(TypedDict):
    pre: str
    post: str

class Rule:
    def __init__(self,
        title: str,
        text: str,
        link: str,
        applyto: str,
    ):
        self.title = title
        self.text = text
        self.link = link
        self.applyto = applyto

class Reddack:
    def __init__(self,
        subreddit_name: str,
        praw_auth: PrawAuth,
        slack_auth: SlackAuth,
        channels: dict[ReddackItem, Channels],
        rules: dict[str, Rule],
        known_items_path: Union[Path, str] = Path.cwd() / 'KNOWN_ITEMS.json',
        post_requests_path: Union[Path, str] = Path.cwd() / 'POST',
        thresholds: dict[ReddackItem, Thresholds] = {
            ReddackSubmission: {
                'approve': +1,
                'remove': -1
            },
            ReddackComment: {
                'approve': +1,
                'remove': -1
            }
        },
        removal_template: RemovalTemplate = None
    ):
        self.subreddit_name = subreddit_name
        self.praw_auth = praw_auth
        self.slack_auth = slack_auth
        self.known_items_path = known_items_path
        self.post_requests_path = post_requests_path
        self.rules = rules
        self.channels = channels
        self.thresholds = thresholds
        self._removal_template = removal_template

    @property
    def subreddit(self):
        return self.praw_auth.create_client().subreddit(self.subreddit_name)

    @property
    def praw_client(self):
        return self.praw_auth.create_client()

    @property
    def slack_client(self):
        return self.slack_auth.create_client()

    @property
    def slack_user_client(self):
        return self.slack_auth.create_client(as_user=True)
    
    def removal_message(self, rule):
        return "Removal message here"

def removal_message(
    template: RemovalTemplate, 
    rules: list[Rule], 
    mod_note: str = None
):
    msg = template['pre']
    for rule in rules:
        msg += "\n\n> " + rule.text
    msg += mod_note
    msg += template['post'] 
    
