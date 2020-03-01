# 🤖 PrimerBot

A Slackbot that makes documentation easier! PrimerBot connects to a channel and automatically sends messages in a slack channel to a linked Notion database. 

**Features:**
- Supports two message parsing modes: 'all' (all messages get sent) and 'link' (only messages with URLs get sent)
- Threads are tracked in Notion Page
- Messages can be added/removed from notion using a react
- Priority of message can be marked using reacts

### Example

The following slack message will create the row in the linked notion database below!
<p float="left">
  <img src="https://imgur.com/souAJnJ.png" width="300" />
  ->
  <img src="https://imgur.com/ye89LD4.png" width="500" /> 
</p>

Any comments threaded on the slack message, will similarly be sent to the Notion page!
<p float="left">
  <img src="https://imgur.com/whRG8Wi.png" width="300" />
  ->
  <img src="https://imgur.com/tx3U3qp.png" width="500" /> 
</p>

## Setup

1. Create a new Slackbot in your workspace on the Slack API Webiste

Necessary Scopes: 
- channels:history
- channels:read
- chat:write
- reactions:read
- reactions:write
- users:read

Necessary Event Subscriptions: 
- message.channels
- reaction_added

2. Clone this repo and set up the appropriate environment variables

**Environment Variables**
```
SLACK_AUTH_TOKEN= <Found under "Oauth & Permissions">
SLACK_SIGNING_SECRET= <Found under "Basic Information">
NOTION_AUTH_TOKEN= <Login to Notion on web, and take value from cookie named "token_v2">
```

3. Create a relevant settings file using structure described below

4. Deploy code to server (like heroku) and setup Event URL on Slackbot API Website

5. Invite Slackbot to channels and start using!

## settings.json

Sample Settings.json file: 

```
{
  "channelRules": {
    "references": {
      "notionBaseUrl": "https://www.notion.so/withprimer/ce249a64e8524c79baaef8dbe565763b?v=4540f17ca3d1432192bb0f927305a8ed",
      "messageTrigger": "link",
      "reactions": {
        "ack": "floppy_disk",
        "normalPriority": "heavy_plus_sign",
        "highPriority": "exclamation",
        "veryHighPriority": "bangbang",
        "saveMessage": "inbox_tray",
        "unsaveMessage": "outbox_tray"
      },
      "fieldNames": {
        "title": "Title",
        "priority": "Importance",
        "user": "Sourcer",
        "link": "Link"
      }
    }
  }
}
```
For each channel that you want PrimerBot to watch, add a new property in `channelRules` with the name of the channel. Below is an explanation of each of the properties for each channel

`notionBaseUrl`: This is the URL of the database you want to send data to (right-click and press "copy link" to get this URL from notion)

`messageTrigger`: This determines which type of messages PrimerBot will respond to. Options are "all" (which sends all messages) and "link" (which only sends messages with links)

`reactions`: Emojis used to react and control Primerbot

- `ack`: This is the emoji Primerbot uses to note that it has saved a message in notion
- `Xpriority`: These three emojis are used to denote the priority of a row 
- `saveMessage`: This emoji react can be used to save an otherwise untracked message in Slack (it will not pick up existing threaded messages)
- `unsaveMessage`: This emoji react can be used to unsave a currently tracked message in Slack


`fieldNames`: PrimerBot sends data to notion using these column titles

- `title`: This is the primary key of the table. When `messageTrigger` is set to Link, this will be the title of the URL. Otherwise it'll just be the message
- `priority`: Column name for priority delineation. Must be a single-select with options "Normal", "High", and "Very High" in Notion
- `user`: This is the column name where the user who sent the message will be saved
- `link`: If the trigger is a link, this is where the URL will be saved.
