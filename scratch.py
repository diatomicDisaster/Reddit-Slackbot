#Temporary file for checking whether things work or not

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import payload
import json
import praw
import logging
logging.basicConfig(level=logging.DEBUG)

slack_token = os.environ.get('SLACK_TOKEN')
client = WebClient(token=slack_token)

reddit = praw.Reddit(
    client_id=os.environ.get('PRAW_CLIENT_ID'),
    client_secret=os.environ.get('PRAW_CLIENT_SECRET'),
    password=os.environ.get('PRAW_PASSWORD'),
    username="GenericTesting",
    user_agent="Testing bot"
)

rspacex = reddit.subreddit("generictesting")

for item in rspacex.mod.modqueue(limit=None):
    if isinstance(item, praw.models.Submission):
        try:
            result = client.chat_postMessage(
                channel="C02V3G9AZJ6",
                blocks=json.dumps(
                    payload.submission_msg_payload(
                        item.created_utc,
                        f"<{item.url}|{item.title}>",
                        f"<https://reddit.com/u/{item.author.name}|u/{item.author.name}>",
                        item.thumbnail,
                        f"https://reddit.com{item.permalink}"
                    )
                    #payload.simple_payload(item.title)
                ),
                unfurl_links=False,
                unfurl_media=False
            )
        except SlackApiError as e:
            print(f"Error: {e}")

