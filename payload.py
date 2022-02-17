from datetime import datetime, timezone
import json
import os

from config import POST_DIR

class ModResponse:
    """Class for storing moderator responses to Slack mod item messages"""
    ## Find a cleaner, more general way of updating mod response actions
    def __init__(self, parentmsg_ts):
        self.parentmsg_ts = parentmsg_ts
        self.actions = {
            'actionApproveRemove' : None,
            'actionRemovalReason' : [],
            'actionConfirm' : False
            }

    def update(self, state):
        for block in state.values.values():
            for actionid, action in block.items():
                if actionid == "actionRemovalReason":
                    self.actions[actionid].append(action.value)
                else:
                    self.actions[actionid] = action.value



def find_latest(message_ts):
    """Retrieves the latest POST request timestamp for a given message."""
    latest_ts = message_ts
    for postfile in os.listdir(os.fsencode(POST_DIR)):
        filename = os.fsdecode(postfile)
        if filename.endswith(".json"):
            request_ts = filename.strip(".json")
            if request_ts < latest: 
                continue
            else:
                with open(os.path.join(POST_DIR, filename), 'r') as file:
                    payload = json.load(file)
                if payload['container']['message_ts'] == message_ts:
                    if request_ts > latest : latest = request_ts
                else:
                    continue
        else:
            continue
    return latest_ts

def find_payloads(message_ts):
    """Retrieves all POST request timestamps for a given message."""
    payload_ts = []
    for postfile in os.listdir(os.fsencode(POST_DIR)):
        filename = os.fsdecode(postfile)
        if filename.endswith(".json"):
            request_ts = filename.strip(".json")
            with open(os.path.join(POST_DIR, filename), 'r') as file:
                payload = json.load(file)
            if payload['container']['message_ts'] == message_ts:
                payload_ts.append(request_ts)
            else:
                continue
        else:
            continue
    return payload_ts.sort()

def build_submission_blocks(
    created_unix, title, url, authorname, thumbnail_url, permalink):
    """Build Slack API blocks for new submission message."""
    # TODO Dynamically generate blocks based on user-defined config file with
    #  custom subreddit removal messages.
    # TODO Add block element for flairing posts functionality.
    
    # Dictionary of month names
    months = {
        1: 'January', 2: 'February', 3: 'March',
        4: 'April', 5: 'May', 6: 'June', 7: 'July',
        8: 'August', 9: 'September', 10: 'October',
        11: 'November', 12: 'December'
        }

    # Lambda function for converting cardinal to ordinal
    ordinal = lambda n : "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

    # Convert PRAW object attributes to message strings
    timestamp = datetime.fromtimestamp(created_unix, tz=timezone.utc)
    timestring = f"Created {months[timestamp.month]} {ordinal(timestamp.day)}  at {timestamp:%H:%M}"
    titlestring = f"<{url}|{title}>"
    authorstring = f"Author: <https://reddit.com/u/{authorname}|u/{authorname}>"
    permalinkstring = f"https://reddit.com{permalink}"
    
    # Slack API blocks
    blocks = [
        # Preamble
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "<!channel> New modqueue item:"
            }
        },
        {
            "type": "divider"
        },
        # Date and time context
        {
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": timestring
                }
            ]
        },
        # Submission info
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": titlestring
            }
        },
		{
			"type": "image",
			"image_url": thumbnail_url,
			"alt_text": "thumbnail"
		},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": authorstring
                }
            ]
        },
        # Moderator actions
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "See Post",
                        "emoji": True
                    },
                    "value": "seepost",
                    "url": permalinkstring,
                    "action_id": "actionSeePost"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "radio_buttons",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Approve",
                                "emoji": True
                            },
                            "value": "approve"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Remove",
                                "emoji": True
                            },
                            "value": "remove"
                        }
                    ],
                    "action_id": "actionApproveRemove"
                }
            ]
        },
        # Removal reasons
        {
            "type": "input",
            "element": {
                "type": "multi_static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select options",
                    "emoji": True
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q1 (Respectful): Hostility or personal attacks",
                            "emoji": True
                        },
                        "value": "Q1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q1.3 (Respectful - Policy): Plagiarism, spam, misleading or illegality.",
                            "emoji": True
                        },
                        "value": "Q1.3"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q2.1 (Relevant - Focused): Not about SpaceX (generic)",
                            "emoji": True
                        },
                        "value": "Q2.1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q2.1.1 (Relevant - Focused - Lounge): Tangential matters to Lounge",
                            "emoji": True
                        },
                        "value": "Q2.1.1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q2.1.2 (Relevant - Focused - Starlink): Minor Starlink news to r/Starlink",
                            "emoji": True
                        },
                        "value": "Q2.1.2"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q2.1.3 (Relevant - Focused - NASA): NASA matters to r/NASA",
                            "emoji": True
                        },
                        "value": "Q2.1.3"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q2.2 (Relevant - Specific): Fanart, fandom, jobs, meta and speculation",
                            "emoji": True
                        },
                        "value": "Q2.2"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q3.1 (Novel - Salient): Duplicates or not enough new info",
                            "emoji": True
                        },
                        "value": "Q3.1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q3.2 (Novel - Tweetstorm): Tweetstorms to original thread",
                            "emoji": True
                        },
                        "value": "Q3.2"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q3.3 (Novel - Question): Simple questions to wiki, FAQ, or Google",
                            "emoji": True
                        },
                        "value": "Q3.3"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q3.4 (Novel - Current): Out of date or anniversary posts ",
                            "emoji": True
                        },
                        "value": "Q3.4"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q4.1 (Substantive - Meme): Jokes, memes, and pop culture to Masterrace",
                            "emoji": True
                        },
                        "value": "Q4.1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q4.2 (Substantive - Contribute): Low-quality posts to Lounge",
                            "emoji": True
                        },
                        "value": "Q4.2"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q4.3 (Substantive - Factual): Speculation, inflammatory or lacking evidence",
                            "emoji": True
                        },
                        "value": "Q4.3"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q4.4 (Substantive - Reddiquite): Bad Reddiqute",
                            "emoji": True
                        },
                        "value": "Q4.4"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q4.5 (Substantive - Personal): Non-newsworthy, opinion, photos or fluff",
                            "emoji": True
                        },
                        "value": "Q4.5"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q5.1 (Wellformed - Format): Formatting issues or bad crosspost",
                            "emoji": True
                        },
                        "value": "Q5.1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q5.2 (Wellformed - Title): Clickbait, bad or non-matching titles",
                            "emoji": True
                        },
                        "value": "Q5.2"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q5.3 (Wellformed - Link): Broken, dirty, AMP or paywalled links",
                            "emoji": True
                        },
                        "value": "Q5.3"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q5.4 (Wellformed - Discuss): Straightforward/general questions",
                            "emoji": True
                        },
                        "value": "Q5.4"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q5.5.1 (Wellformed - Thread - Launch): Launch thread updates and questions",
                            "emoji": True
                        },
                        "value": "Q5.5.1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q5.5.2 (Wellformed - Thread - Media): Media thread photos and articles",
                            "emoji": True
                        },
                        "value": "Q5.5.2"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q5.5.3 (Wellformed - Thread - Campaign): Campaign updates and questions",
                            "emoji": True
                        },
                        "value": "Q5.5.3"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Q5.5.4 (Welformed - Thread - Starship): Starship dev updates",
                            "emoji": True
                        },
                        "value": "Q5.5.4"
                    }
                ],
                "action_id": "actionRemovalReason"
            },
            "label": {
                "type": "plain_text",
                "text": "Select removal reason(s):",
                "emoji": True
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Confirm",
                        "emoji": True
                    },
                    "value": "confirmed",
                    "action_id": "actionConfirm"
                }
            ]
        }
    ]
    return blocks