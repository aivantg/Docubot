from dotenv import load_dotenv
from pprint import pprint
import requests as r
from utils.notionUtils import create_notion_row, delete_notion_row, add_comment_to_notion_row, update_properties_on_notion_row
from utils.db import find_tracked_message, track_message, untrack_message
import json
import os
import slack

load_dotenv()

SLACK_TOKEN = os.getenv('SLACK_AUTH_TOKEN')
IDEAS_DB = "https://www.notion.so/withprimer/0f48f4075423407390f99214db3dc6bf?v=f88e7fa4a2e14658be434bec68e9db9d"
client = slack.WebClient(token=SLACK_TOKEN)
BOT_ID = client.auth_test()['user_id']

# Translate channels in settings.json from name to ID
with open('utils/settings.json') as f:
  settings = json.load(f)
  data = r.get("https://slack.com/api/conversations.list?token=" + SLACK_TOKEN).json()
  watched_channels = {c['id']: c['name'] for c in data['channels'] if settings['channelRules'].get(c['name'])}
  
# Utility Functions
def send_message(channel, message, thread_ts=None):
    try: 
        return client.chat_postMessage(channel=channel, text=message, thread_ts=thread_ts, unfurl_media="False")['ts']
    except:
        print("Could not send message")

def remove_message(channel, ts):
    try:
        client.chat_delete(channel=channel, ts=ts)
    except:
        print("Could not remove message")

def react_message(channel, ts, reaction):
    try: 
        client.reactions_add(channel=channel, timestamp=ts, name=reaction)
    except:
        print("Could not add Reaction")

def unreact_message(channel, ts, reaction):
    try: 
        client.reactions_remove(channel=channel, timestamp=ts, name=reaction)
    except:
        print("Could not remove Reaction")

def get_username(userId):
    return client.users_info(user=userId)['user']['profile']['real_name']

def get_slack_message(channel, ts):
    return client.conversations_history(latest=ts, channel=channel, limit=1, inclusive="True")['messages'][0]

def save_message_to_notion(ts, channel, parameters):
    react_message(channel, ts, 'floppy_disk')
    row_id = create_notion_row(IDEAS_DB, parameters)
    notion_link_ts = send_message(channel, "Notion Link: https://www.notion.so/withprimer/" + row_id, ts)
    track_message(ts, channel, row_id, notion_link_ts)

def remove_message_from_notion(message):
    unreact_message(message.channel, message.ts, 'floppy_disk')
    delete_notion_row(IDEAS_DB, message.notion_row_id)
    remove_message(message.channel, message.notion_link_ts)
    untrack_message(message.ts, message.channel)

def set_priority(message, priority):
    update_properties_on_notion_row(IDEAS_DB, message.notion_row_id, {"Importance": priority})

# Event Handlers
def process_message(event):
    text, channel, ts, user, thread_ts = event.get('text'), event.get('channel'), event.get('ts'), event.get('user'), event.get('thread_ts')
    if channel in watched_channels and user and user != BOT_ID:
        if thread_ts:
            message = find_tracked_message(thread_ts, channel)
            if message:
                # TODO: Figure out how to save comments in threads
                # add_comment_to_notion_row(IDEAS_DB, message.notion_row_id)
                pass
        else:
            save_message_to_notion(ts, channel, {'idea': text, 'author': get_username(user), 'Importance': 'Normal'})


def process_reaction(event):
    reaction, channel, user, ts = event['reaction'], event['item']['channel'], event['user'], event['item']['ts']
    if channel in watched_channels and user != BOT_ID:
        message = find_tracked_message(ts, channel)
        if message:
            if reaction == 'outbox_tray':
                remove_message_from_notion(message)
            if reaction == 'exclamation':
                set_priority(message, "High")
            if reaction == "bangbang":
                set_priority(message, "Very High")
        else:
            if reaction == 'inbox_tray':
                slack_message = get_slack_message(channel, ts)
                text, user = slack_message['text'], slack_message['user']
                save_message_to_notion(ts, channel, {'idea': text, 'author': get_username(user), 'Importance': 'Normal'})

