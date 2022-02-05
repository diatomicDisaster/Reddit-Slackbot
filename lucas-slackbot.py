import os
import time
import json
import removal
import praw
from slackclient import SlackClient
import urllib.request, json 
def sendMsg(item,channel,ping):
    print(item)
    title = item.title
    print("Sending Slack Message: "+title)
    pingText = ""
    if ping:
        pingText="<!channel> "
    if "/u/" in title:
        title = "Comment: "+title
    text = ""
    if item.is_self:
        text = item.selftext
    if not item.is_self:
        text =text +"\n"+item.url
    attach = json.dumps([{"ts":item.created_utc,"text":text,"title":title,"thumb_url": item.thumbnail,"author_name":item.author.name,"title_link": "https://reddit.com"+item.permalink,"fallback":"Error","color":"#3AA3E3", "author_link": "https://reddit.com/u/"+item.author.name,"attachment_type":"default"}])
    output = sc.api_call("chat.postMessage",channel=channel,text=pingText+item.title,attachments=attach,link_names=True,icon_url="https://pbs.twimg.com/media/DvjA8u-U0AEaI-u.jpg",as_user=True )
    
    timestamp = output["ts"]
    print(timestamp)
    return timestamp
def sendMsgSimple(msg,channel,ping):
    print("Sending Votes Message")
    title= "Votes"
    pingText =""
    if ping:
        pingText="<!channel> "
    if "/u/" in title:
        title = "Comment: "+title
    output= sc.api_call("chat.postMessage",channel=channel,text=pingText+msg,link_names=True,icon_url="https://pbs.twimg.com/media/DvjA8u-U0AEaI-u.jpg",as_user=True )
    timestamp=0
    if "ts" in output:
        timestamp = output["ts"]
    print(timestamp)
    return timestamp


def ping(ts,item):
    print("Pinging")
    sc.api_call("chat.update",ts=ts,channel=channel_new,text="<!channel> "+item.title)


def loadReactions(ts):
    output= sc.api_call("reactions.get",channel=channel_new,timestamp=ts)
    return output


def checkReaction(ts,name):
    rm = loadReactions(ts)
    if "message" not in rm:
        print(str(rm))

    if "reactions" not in rm["message"]:
        return 0
    reactions = rm["message"]["reactions"]
    for react in reactions:
        if react["name"] == name:
            return react["count"]
    time.sleep(1)
    return 0


def checkReaction(ts,name,rm):
    if "message" not in rm:
        print(str(rm))
        return -1
    if "reactions" not in rm["message"]:
        return 0
    reactions =rm["message"]["reactions"]
    for react in reactions:
        if react["name"] == name:
            return react["count"]
    time.sleep(1)
    return 0


def checkReactionToMSG(ts):
    print("Building Reactions Message")
    rm = loadReactions(ts)
    print(rm,flush=True)
    if "reactions" not in rm["message"]:
        return ""
    reactions =rm["message"]["reactions"]
    s = "*Votes on this Post*:\n"
    for react in reactions:
        s = s + ":" + react["name"] + ":"
        for user in react["users"]:
            s = s + users[user] + ", "
        s = s[:-2]+"\n"
    return s


def removeMessageAPI(ts,channel_src="CGZ9ZQD37"):
    print("Removing Message")
    out=scA.api_call('chat.delete', channel=channel_src, ts=ts)
    print(out)


def cleanChannel():
    output= scA.api_call("conversations.history",channel=channel_new)
    print(output)
    for msg in output["messages"][:4]:
        removeMessageAPI(msg["ts"])
        print(msg["ts"])


def cleanReplies(ts):
    print("Cleaning Replies")
    for reply in getRepliesTS(ts):
        removeMessageAPI(reply)


def getRepliesTS(ts):
    replies = []
    print("getting Replies")
    output = scA.api_call("conversations.replies", channel=channel_new, ts=ts)
    print(output)
    if "messages" not in output or len(output["messages"])==1:
        return replies
    for message in output["messages"][1:]:
        replies.append(message["ts"])
    print(replies)
    return replies


def getTexts(ts):
    texts = []
    output = scA.api_call("conversations.replies", channel=channel_new, ts=ts)
    if "messages" not in output:
        return
    for message in output["messages"][1:]:
        texts.append(message["text"])
    return texts
def getTextsFormatted(ts):
    formatted=""
    output = scA.api_call("conversations.replies", channel=channel_new, ts=ts)
    if "messages" not in output:
        return "NONE"
    for message in output["messages"][1:]:
        formatted=formatted+users[message["user"]]+" : "+message["text"]+"\n"
    return formatted

def getModNote(ts):
    note=""
    messages= getTexts(ts)
    print(messages)
    if messages is None:
        return ""
    for message in messages:
        up= str(message).upper()
        if up.startswith("@MN"):
            note = message[3:]
    return note
def sendReminder(item):
    title =item.title+" needs moderation in #newposts!"
    output = sendMsgSimple(title,channel_reminder,True)
    return output


slack_token_bot = "Something Long goes here"
slack_token_auth = "Another long thing"
channel_new = "CGZ9ZQD37"
channel_old = "CGC64GRS9"
channel_reminder = "CK1ARE4A0"
sc = SlackClient(slack_token_bot)
scA = SlackClient(slack_token_auth)
#depricated _ura ="hts="
#depricated _urb = "&pretty=1"
users = {"U01GDH317N0":"modehopper"}
