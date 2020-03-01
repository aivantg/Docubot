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

def save_message_to_notion(ts, channel, text, user, priority, link, channel_settings):
    # Create Row in Notion Database
    names = channel_settings['fieldNames']
    row_data = { names['title']: text, names['user']: user, names['priority']: priority }
    if link:
        row_data[names['link']] = link
    row_id = create_notion_row(channel_settings['notionBaseUrl'], row_data)

    # Share info in Slack
    react_message(channel, ts, channel_settings['reactions']['ack'])
    notion_link_ts = send_message(channel, "Notion Link: https://www.notion.so/" + settings['notionBase'] + "/" + row_id, ts)
    
    # Save Tracked Message to Database
    track_message(ts, channel, row_id, notion_link_ts)

def remove_message_from_notion(message, channel_settings):
    unreact_message(message.channel, message.ts, channel_settings['reactions']['ack'])
    delete_notion_row(channel_settings['notionBaseUrl'], message.notion_row_id)
    remove_message(message.channel, message.notion_link_ts)
    untrack_message(message.ts, message.channel)

def set_priority(message, priority, channel_settings):
    priority_data = {channel_settings['fieldNames']['priority']: priority}
    update_properties_on_notion_row(channel_settings['notionBaseUrl'], message.notion_row_id, priority_data)

# Event Handlers

def process_message(text, channel, ts, user, thread_ts, channel_settings):
    if thread_ts:
            message = find_tracked_message(thread_ts, channel)
            if message:
                # TODO: Figure out how to save threaded message on the notion page
                # add_comment_to_notion_row(IDEAS_DB, message.notion_row_id)
                pass
    else:
        save_message_to_notion(ts, channel, text, get_username(user), 'Normal', None, channel_settings)

def process_reaction(reaction, channel, ts, user, channel_settings):
    names, reacts = channel_settings['fieldNames'], channel_settings['reactions']
    message = find_tracked_message(ts, channel)
    if message:
        if reaction == reacts['unsaveMessage']:
            remove_message_from_notion(message, channel_settings)
        if reaction == reacts['normalPriority']:
            set_priority(message, "Normal", channel_settings)
        if reaction == reacts['highPriority']:
            set_priority(message, "High", channel_settings)
        if reaction == reacts['veryHighPriority']:
            set_priority(message, "Very High", channel_settings)
    else:
        if reaction == reacts['saveMessage']:
            slack_message = get_slack_message(channel, ts)
            text, user = slack_message['text'], slack_message['user']
            save_message_to_notion(ts, channel, text, get_username(user), 'Normal', None, channel_settings)


def receive_message(event):
    if not event.get('text'): # Edge case
        return 
    text, channel, ts, user, thread_ts = event['text'], event['channel'], event['ts'], event['user'], event.get('thread_ts')
    channel_name = watched_channels.get(channel)
    if user and user != BOT_ID and channel_name:
        channel_settings = settings['channelRules'][channel_name]
        process_message(text, channel, ts, user, thread_ts, channel_settings)
        


def receive_reaction(event):
    reaction, channel, user, ts = event['reaction'], event['item']['channel'], event['user'], event['item']['ts']
    channel_name = watched_channels.get(channel)
    if user and user != BOT_ID and channel_name:
        channel_settings = settings['channelRules'][channel_name]
        process_reaction(reaction, channel, ts, user, channel_settings)
        
