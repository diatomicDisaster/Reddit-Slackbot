
import abc
from typing import Type

import praw

from modfromslack.messaging import newitem_message
from modfromslack.payload import build_submission_blocks
from modfromslack.exceptions import MsgSendError, ActionSequenceError
from modfromslack.config import APPROVAL_THRESHOLD, REMOVAL_THRESHOLD

class AbstractModAction(abc.ABC):
    """Abstract class for moderation actions."""
    @abc.abstractmethod
    def update(self):
        pass

class ModAction(AbstractModAction):
    def __init__(self):
        self.timestamp = "0"

    def update(self, action):
        if action['action_ts'] == self.timestamp:
            print("Ignoring action with identical timestamp")
            return
        elif action['action_ts'] < self.timestamp:
            print("Ignoring action with older timestamp")
            return
        else:
            return self._update(action)

class ApproveRemove(ModAction):
    """Mod action defining approve or remove action."""
    def __init__(self):
        self.value = None
        super().__init__()

    def update(self, action):
        self.value = action['selected_option']['value']

class RemovalReason(ModAction):
    """Mod action defining removal reasons."""
    def __init__(self):
        self.value = []
        super().__init__()
    
    def update(self, action):
        self.value = [option['value'] for option in action['selected_options']]

class Confirm(ModAction):
    """Mod action confirming selection."""
    def __init__(self):
        self.value = False
    
    def update(self, action):
        """Confirm previous inputs"""
        self.value = True

class SubmissionResponse:
    """Class for storing moderator responses to Slack mod item messages."""
    def __init__(self, parentmsg_ts):
        self.parentmsg_ts = parentmsg_ts
        self.actions = {
            'actionApproveRemove' : ApproveRemove(),
            'actionRemovalReason' : RemovalReason(),
            'actionConfirm' : Confirm()
            }
        self.confirmed = False

    def update(self, payload_actions):
        """Update response with actions from Slack payload."""
        for action in payload_actions:
            if action['action_ts'] < self.parentmsg_ts:
                raise ActionSequenceError(
                    "parent message", 
                    "action",
                    afterword="Something went wrong when updating responses, "
                    "if app has rebooted, try clearing known item JSON file."
                    )
            self.actions[action['action_id']].update(action)

class ModItem(object):
    """Stores information about the state of an item in the modqueue."""
    def __init__(self, prawitem):
        self.prawitem = prawitem.id
        self.message_ts = None
        self.responses = {}

class ModSubmission(ModItem):
    """Stores information about the state of a submission in the modqueue."""

    _approval_threshold : float = APPROVAL_THRESHOLD
    _removal_threshold : float = REMOVAL_THRESHOLD
    ResponseType : Type = SubmissionResponse

    def __init__(self, prawitem):
        self.created_utc = prawitem.created_utc 
        self.title = prawitem.title
        self.url = prawitem.url
        self.author = prawitem.author.name
        self.thumbnail = prawitem.thumbnail
        self.permalink = prawitem.permalink
        super().__init__(prawitem)

    def send_msg(self, client, channel):
        result = newitem_message(self.msg_payload, client, channel)
        self.message_ts = result.data['ts']
    
    @property
    def msg_payload(self):
        try:
            return build_submission_blocks(
                self.created_utc, 
                self.title, 
                self.url, 
                self.author, 
                self.thumbnail, 
                self.permalink
            )
        except AttributeError as error:
            raise MsgSendError(
                f"{error.obj!r} object is missing field {error.name!r}."
            ) from error

    @property
    def approve_or_remove(self):
        votesum = 0
        for response in self.responses.values():
            votesum += float(response.actions['actionApproveRemove'].value)
        if votesum >= self._approval_threshold:
            return "approve"
        elif votesum <= self._removal_threshold:
            return "remove"
        else:
            return None

    @property
    def removal_reasons(self):
        unique_reasons = []
        for response in self.responses:
            for reason in response.actions['actionRemovalReason'].value:
                if reason not in unique_reasons: unique_reasons.append(reason)
        return sorted(unique_reasons)
