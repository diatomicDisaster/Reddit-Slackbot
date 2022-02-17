import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from exceptions import MsgSendError

slack_token = os.environ.get('SLACK_TOKEN')
client = WebClient(token=slack_token)

def newitem_message(blocks, channel):
    """Send message for new mod item to specified Slack channel"""
    ### Handle missing thumbnail URL gracefully, as many third party sources
    #  do not appear to permalink thumbnails.
    try:
        result = client.chat_postMessage(
            blocks=blocks, channel=channel, text="New modqueue item", 
            unfurl_links=False, unfurl_media=False
        )
        result.validate()
        return result.ts
    except SlackApiError as error:
        raise MsgSendError("Failed to send item to Slack.") from error
