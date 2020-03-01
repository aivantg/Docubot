from peewee import *
import datetime

db = SqliteDatabase('bot.db')

class BaseModel(Model):
    class Meta:
        database = db

class TrackedMessage(BaseModel):
    ts = CharField(unique=True)
    channel = CharField()
    notion_row_id = CharField()
    notion_link_ts = CharField()

def setup_db():
    db.connect()
    db.create_tables([TrackedMessage])

def track_message(ts, channel, row_id, notion_link_ts):
    return TrackedMessage.create(ts=ts, channel=channel, notion_row_id=row_id, notion_link_ts=notion_link_ts)

def find_tracked_message(ts, channel):
    try: 
        return TrackedMessage.get(TrackedMessage.ts == ts, TrackedMessage.channel == channel)
    except:
        print("Could not find message.")

def untrack_message(ts, channel):
    return find_tracked_message(ts, channel).delete_instance()