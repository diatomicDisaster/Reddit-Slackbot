import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from exceptions import MsgSendError

slack_token = os.environ.get('SLACK_TOKEN')
client = WebClient(token=slack_token)

def newitem_message(blocks, channel):
    try:
        result = client.chat_postMessage(
            blocks=blocks, channel=channel, 
            unfurl_links=False, unfurl_media=False,
            text="New modqueue item"
        )
        result.validate()
    except SlackApiError as error:
        raise MsgSendError("Failed to send item to Slack.") from error