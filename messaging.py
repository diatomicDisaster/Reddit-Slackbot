# 3rd party imports
from slack_sdk.errors import SlackApiError

# Local imports
from modfromslack.exceptions import MsgSendError

def newitem_message(blocks, client, channel):
    """Send message for new mod item to specified Slack channel"""
    # TODO Handle missing thumbnail URL gracefully, as many third party sources
    #  do not appear to permalink thumbnails.
    try:
        result = client.chat_postMessage(
            blocks=blocks, channel=channel, text="New modqueue item", 
            unfurl_links=False, unfurl_media=False
        )
        result.validate()
        return result
    except SlackApiError as error:
        raise MsgSendError("Failed to send item to Slack.") from error


