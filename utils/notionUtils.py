from notion.client import NotionClient
from notion.block import ToggleBlock, BulletedListBlock
from dotenv import load_dotenv
import os

# Setup Environment Variables
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_AUTH_TOKEN")

# Setup Notion Client
client = NotionClient(NOTION_TOKEN)

def create_notion_row(databaseUrl, properties):
    db = client.get_collection_view(databaseUrl)
    row = db.collection.add_row()
    for key, value in properties.items():
        setattr(row, key, value)
    slack_discussion = row.children.add_new(ToggleBlock, title="**Slack Discussion**")
    return row.id, slack_discussion.id, row.get_browseable_url()

def delete_notion_row(rowId):
    client.get_block(rowId).remove()

def add_comment_to_notion_row(rowId, discussionId, comment, user):
    row = client.get_block(rowId)
    discussion = [b for b in row.children if b.id == discussionId]
    if len(discussion):
        discussion[0].children.add_new(BulletedListBlock, title=user + ": " + comment)
    else:
        print("Can't find Slack Discussion Toggle")

def update_properties_on_notion_row(databaseUrl, rowId, properties):
    row = client.get_block(rowId)
    for key, value in properties.items():
        setattr(row, key, value)

