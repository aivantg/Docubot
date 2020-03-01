from notion.client import NotionClient
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
    return row.id

def delete_notion_row(databaseUrl, rowId):
    client.get_block(rowId).remove()

def add_comment_to_notion_row(databaseUrl, rowId):
    pass

def update_properties_on_notion_row(databaseUrl, rowId, properties):
    row = client.get_block(rowId)
    for key, value in properties.items():
        setattr(row, key, value)

# create_row('https://www.notion.so/withprimer/0f48f4075423407390f99214db3dc6bf?v=f88e7fa4a2e14658be434bec68e9db9d', {'title': 'Hello!', 'link': 'https://www.google.com'})