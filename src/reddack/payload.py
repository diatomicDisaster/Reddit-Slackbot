from datetime import datetime, timezone


# Dictionary of month names
months = {
    1: 'January', 2: 'February', 3: 'March',
    4: 'April', 5: 'May', 6: 'June', 7: 'July',
    8: 'August', 9: 'September', 10: 'October',
    11: 'November', 12: 'December'
}

# Lambda function for converting cardinal to ordinal
ordinal = lambda n : "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])


def build_response_block(name: str, vote, removalreasons: list) -> dict:
    """Build blocks for moderator responses in archive message"""
    textstring = f"{name}: {vote}"
    if removalreasons:
        textstring += "\n\t"
        for reason in removalreasons:
            textstring += f" {reason},"
        textstring = textstring.rstrip(",")
    responseblock = {
        "type": "mrkdwn",
        "text": textstring
    }
    return responseblock

def build_archive_blocks(
    created_unix: str, 
    title: str,
    authorname: str,
    permalink: str,
    responseblocks: dict = None
) -> dict:
    """Build Slack API blocks for archive message."""
    timestamp = datetime.fromtimestamp(created_unix, tz=timezone.utc)
    timestring = f"Created {months[timestamp.month]} {ordinal(timestamp.day)} at {timestamp:%H:%M}"
    titlestring = f"<https://reddit.com{permalink}|{title}>"
    authorstring = f"Author: u/{authorname}"
    if not responseblocks:
        responseblocks = [{
            "type": "mrkdwn",
            "text": "No moderator responses"
        }]
    archiveblocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": titlestring
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": timestring
                }
            ]
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
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Votes on this post:*"
            }
        },
        {
            "type": "section",
            "fields": responseblocks,
        },
        {
            "type": "divider"
        },
    ]
    return archiveblocks

def rule_select_json(value: str, title:str ) -> dict:
    block_json = {
        "text": {
            "type": "plain_text",
            "text": title,
            "emoji": False,
        },
        "value": value
    }
    return block_json

def build_removal_block(rules: list) -> list:
    "Build list of Slack API multi_static_select options for removal reasons"
    removal_options = []
    for name, rule in rules.items():
        option = {
            "text": {
                "type": "plain_text",
                "text": rule["shorttext"],
                "emoji": False
            },
            "value": name
        }
        removal_options.append(option)
    return removal_options

def build_submission_block(
    created_unix: str, 
    title: str, 
    url: str, 
    authorname: str, 
    thumbnail_url: str,
    selftext: str,
    permalink: str,
    removal_options: dict
) -> dict:
    """Build Slack API blocks for new submission message."""
    # TODO Add block element for flairing posts functionality.

    # Convert PRAW object attributes to message strings
    timestamp = datetime.fromtimestamp(created_unix, tz=timezone.utc)
    timestring = f"Created {months[timestamp.month]} {ordinal(timestamp.day)}  at {timestamp:%H:%M}"
    titlestring = f"<{url}|{title}>"
    authorstring = f"Author: <https://reddit.com/u/{authorname}|u/{authorname}>"
    permalinkstring = f"https://reddit.com{permalink}"
    
    # Slack API blocks
    submissionblocks = [
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
        # Submission info
        {
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": timestring
                }
            ]
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
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": titlestring
            }
        },
        # Moderator actions
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
                                "text": "Strong Approve",
                                "emoji": True
                            },
                            "value": "+1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Approve",
                                "emoji": True
                            },
                            "value": "+0.5"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Remove",
                                "emoji": True
                            },
                            "value": "-0.5"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Strong Remove",
                                "emoji": True
                            },
                            "value": "-1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Force Remove",
                                "emoji": True
                            },
                            "value": "-999"
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
                "options": removal_options,
                "action_id": "actionRemovalReason"
            },
            "label": {
                "type": "plain_text",
                "text": "Select removal reason(s):",
                "emoji": True
            }
        },
        # Confirm inputs
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
        },
        # Custom moderator note
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": True,
				"action_id": "actionModnote"
			},
			"label": {
				"type": "plain_text",
				"text": "Add modnote:",
				"emoji": True
			}
		},
        # See post button
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View on Reddit",
                        "emoji": True
                    },
                    "value": "seepost",
                    "url": permalinkstring,
                    "action_id": "actionSeePost"
                }
            ]
        }
    ]
    
    # Handle thumbnail gracefully
    if thumbnail_url == 'self': # Replace with preview for text posts
        submissionblocks.insert(5,
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": selftext[:300] + "..." if len(selftext) > 300 else selftext
                }
            }
        )
    elif not thumbnail_url: # Leave empty if no thumbnail url given
        return submissionblocks
    else:
        submissionblocks.insert(5, 
            {
                "type": "image",
                "image_url": thumbnail_url,
                "alt_text": "thumbnail"
            }
        )
    return submissionblocks