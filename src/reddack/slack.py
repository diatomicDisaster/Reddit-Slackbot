import abc

class AbstractAction(abc.ABC):
    """Abstract class for moderation actions."""
    @abc.abstractmethod
    def update(self):
        pass

class Action(AbstractAction):
    def __init__(self):
        self.timestamp = "0"

    def update(self, action):
        pass

class State(AbstractAction):
    def __init__(self):
        self.timestamp = "0"

    def update(self, action):
        pass

class ApproveRemove(State):
    """Mod action defining approve or remove action."""
    def __init__(self):
        self.value = None
        super().__init__()

    def update(self, state):
        self.value = state['selected_option']['value']

class RemovalReason(State):
    """Mod action defining removal reasons."""
    def __init__(self):
        self.value = []
        super().__init__()
    
    def update(self, state):
        self.value = [option['value'] for option in state['selected_options']]

class Modnote(State):
    """Mod action to add a modnote."""
    def __init__(self):
        self.value = None
        super().__init__()

    def update(self, state):
        """Retrieve modnote"""
        self.value = state['value']
        super().__init__()
        
class Confirm(Action):
    """Mod action confirming selection."""
    def __init__(self):
        self.value = False
        super().__init__()
    
    def update(self, action):
        """Confirm previous inputs"""
        self.value = True