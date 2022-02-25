from datetime import datetime, timezone
# from modfromslack.types import ModSubmission, SubmissionResponse

# def build_response_block(user, response: SubmissionResponse):
#     vote = response.actions['actionApproveRemove'].value
#     textstring = f"- {user}: {vote}"
#     if response.actions['actionRemovalReason'].value:
#         text_string += "\n\t"
#     for reason in response.actions['actionRemovalReason'].value:
#         text_string += f" {reason},"
#     textstring = text_string.rstrip(",")
#     responseblock = {
#         "type": "mrkdwn",
#         "text": textstring
#     }
#     return responseblock

# def build_archive_blocks(modsubmission: ModSubmission):
#     responselist = []
#     for user, response in modsubmission.responses.items():
#         responseblock = build_response_block()
#         responselist.append(responseblock)
#     archiveblocks = {
#         "blocks": [
#             {
#                 "type": "context",
#                 "elements": [
#                     {
#                         "type": "plain_text",
#                         "text": "1st January 1970"
#                     }
#                 ]
#             },
#             {
#                 "type": "section",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": "<https://reddit.com/r/spacex|An example title>"
#                 }
#             },
#             {
#                 "type": "context",
#                 "elements": [
#                     {
#                         "type": "mrkdwn",
#                         "text": "u/ModeHopper"
#                     }
#                 ]
#             },
#             {
#                 "type": "divider"
#             },
#             {
#                 "type": "section",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": "*Votes on this post:*"
#                 }
#             },
#             {
#                 "type": "section",
#                 "fields": responselist
#             }
#         ]
#     }


def build_submission_blocks(
    created_unix, 
    title, 
    url, 
    authorname, 
    thumbnail_url, 
    permalink
):
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
                            "value": "1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Remove",
                                "emoji": True
                            },
                            "value": "-1"
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
    return submissionblocks