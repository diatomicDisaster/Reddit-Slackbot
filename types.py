
import abc
import os
from typing import Type

from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient

from modfromslack.payload import (
    build_submission_blocks, 
    build_response_block, 
    build_archive_blocks
)
from modfromslack.exceptions import MsgSendError, ActionSequenceError
from modfromslack.config import (
    APPROVAL_THRESHOLD, 
    REMOVAL_THRESHOLD, 
    SUBMISSION_CHANNEL,
    ARCHIVE_CHANNEL
)

import jsonpickle

# TODO Add functionality for flairing posts
# TODO Add functionality for awarding posts

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

    # def _update(self, action):
    #     self.value = action['selected_option']['value']
    def update(self, state):
        self.value = state['selected_option']['value']

class RemovalReason(ModAction):
    """Mod action defining removal reasons."""
    def __init__(self):
        self.value = []
        super().__init__()
    
    # def _update(self, action):
    #     self.value = [option['value'] for option in action['selected_options']]
    def update(self, state):
        self.value = [option['value'] for option in state['selected_options']]

class Modnote(ModAction):
    """Mod action to add a modnote."""
    def __init__(self):
        self.value = None
        super().__init__()

    def update(self, state):
        """Retrieve modnote"""
        self.value = state['value']
        super().__init__()
        
class Confirm(ModAction):
    """Mod action confirming selection."""
    def __init__(self):
        self.value = False
        super().__init__()
    
    def _update(self, action):
        """Confirm previous inputs"""
        self.value = True

class EmptyAction(ModAction):
    """Mod action that requires nothing."""
    def _update(self, action):
        pass

class SubmissionResponse:
    """Class for storing moderator responses to Slack mod item messages."""
    def __init__(self, parentmsg_ts):
        self.parentmsg_ts = parentmsg_ts
        self.actions = {
            #'actionApproveRemove' : ApproveRemove(),
            #'actionRemovalReason' : RemovalReason(),
            'actionConfirm' : Confirm(),
            'actionSeePost' : EmptyAction()
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
    submissionchannel : str = SUBMISSION_CHANNEL
    archivechannel : str = ARCHIVE_CHANNEL
    _ResponseType : Type = SubmissionResponse

    def __init__(self, prawitem):
        self.created_utc = prawitem.created_utc 
        self.title = prawitem.title
        self.url = prawitem.url
        self.author = prawitem.author.name
        self.thumbnail = prawitem.thumbnail
        self.permalink = prawitem.permalink
        super().__init__(prawitem)

    def send_msg(self, client):
        """Send message for new mod item to specified Slack channel"""
        # TODO Handle missing thumbnail URL gracefully, as many third party 
        # sources do not appear to permalink thumbnails.
        try:
            result = client.chat_postMessage(
                blocks=self.msg_payload, channel=self.submissionchannel, 
                text="New modqueue item", unfurl_links=False, unfurl_media=False
            )
            result.validate()
            self.message_ts = result.data['ts']
            return result
        except SlackApiError as error:
            raise MsgSendError("Failed to send item to Slack.") from error

    def _delete_msg(self, client):
        """Delete replies to mod item message"""
        response = client.conversations_replies(
            channel=self.submissionchannel, 
            ts=self.message_ts
        )
        user_client = WebClient(token=os.environ.get("SLACK_USER_TOKEN"))
        for message in response["messages"][::-1]:
            reply_response = user_client.chat_delete(
                channel=self.submissionchannel, 
                ts=message["ts"],
                as_user=True
            )

    def _send_archive(self, client):
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
            blocks=archiveblocks, channel=self.archivechannel,
            text="Archived modqueue item", unfurl_links=False, unfurl_media=False
        )

    def complete_cleanup(self, client):
        """Delete message and send to archive after completion"""
        self._send_archive(client)
        self._delete_msg(client)

    def initialize_response(self, moderator):
        """Initialize a new moderator response object"""
        self.responses[moderator] = self._ResponseType(self.message_ts)

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
            )
    
    @property
    def approve_or_remove(self):
        votesum = 0
        for response in self.responses.values():
            if response.actions['actionConfirm'].value: 
                votesum += float(response.states['actionApproveRemove'].value)
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
            for reason in response.states['actionRemovalReason'].value:
                if reason not in unique_reasons: unique_reasons.append(reason)
        return sorted(unique_reasons)
