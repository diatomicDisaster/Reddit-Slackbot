# Defines the JSON for new submission Slack message payload blocks
import datetime

months = {
    1: 'January', 2: 'February', 3: 'March',
    4: 'April', 5: 'May', 6: 'June', 7: 'July',
    8: 'August', 9: 'September', 10: 'October',
    11: 'November', 12: 'December'
    }

def simple_payload(title):
    blocks = [
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
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Remove",
                                "emoji": True
                            },
                            "value": "value-1"
                        }
                    ],
                    "action_id": "actionApproveRemove"
                }
            ]
        }
    ]
    return blocks

def submission_msg_payload(created_unix, title, author, thumbnail, submission_url):
    timestamp = datetime.datetime.fromtimestamp(created_unix, tz=datetime.timezone.utc)
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
                    "text": f"Created {months[timestamp.month]} {timestamp.day}  at {timestamp:%H:%M:%S}"
                }
            ]
        },
        # Sumbission info
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": title
            }
        },
		{
			"type": "image",
			"image_url": thumbnail,
			"alt_text": "thumbnail"
		},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Author: {author}"
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
                    "url": submission_url,
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
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Remove",
                                "emoji": True
                            },
                            "value": "value-1"
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