import abc

from reddack.exceptions import (
    ActionSequenceError
)

class AbstractAction(abc.ABC):
    """Abstract class for moderation actions."""
    def __new__(cls, *args, **kwargs):
        instance = abc.ABC.__new__(cls)
        instance.timestamp = "0"
        return instance

    @abc.abstractmethod
    def update(self):
        pass

class Action(AbstractAction):
    """Empty action class for e.g buttons"""
    def update(self, action):
        pass

class State(AbstractAction):
    """Stateful action"""
    def update(self, action):
        pass

class ApproveRemove(State):
    """Mod action defining approve or remove action."""
    def __init__(self):
        self.value = None

    def update(self, state):
        self.value = state['selected_option']['value']

class RemovalReason(State):
    """Mod action defining removal reasons."""
    def __init__(self):
        self.value = []
    
    def update(self, state):
        self.value = [option['value'] for option in state['selected_options']]

class Modnote(State):
    """Mod action to add a modnote."""
    def __init__(self):
        self.value = None

    def update(self, state):
        """Retrieve modnote"""
        self.value = state['value']
        
class Confirm(Action):
    """Mod action confirming selection."""
    def __init__(self):
        self.value = False
    
    def update(self, action):
        """Confirm previous inputs"""
        self.value = True


class ReddackResponse(abc.ABC):
    """Class for storing moderator responses to Slack mod item messages"""
    
    @abc.abstractmethod
    def update(self):
        return

class SubmissionResponse(ReddackResponse):
    """Class for storing moderator responses to Slack submission messages."""
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

    def update(self, request: dict, timestamp: str):
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
                    self.states[state].timestamp = timestamp