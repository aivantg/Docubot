from peewee import *
import datetime
import os
import urllib.parse as urlparse


print("DB TESTING")
print(os.environ)

if 'HEROKU' in os.environ:
    import psycopg2
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ["DATABASE_URL"])
    print(url)
    db = PostgresqlDatabase(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
else:
    db = SqliteDatabase('bot.db')

class BaseModel(Model):
    class Meta:
        database = db

class TrackedMessage(BaseModel):
    ts = CharField(unique=True)
    channel = CharField()
    notion_row_id = CharField()
    notion_link_ts = CharField()
    slack_discussion_node = CharField()

def setup_db():
    db.connect()
    db.create_tables([TrackedMessage])

def track_message(ts, channel, row_id, notion_link_ts, discussion_id):
    return TrackedMessage.create(ts=ts, channel=channel, notion_row_id=row_id, notion_link_ts=notion_link_ts, slack_discussion_node=discussion_id)

def find_tracked_message(ts, channel):
    try: 
        return TrackedMessage.get(TrackedMessage.ts == ts, TrackedMessage.channel == channel)
    except:
        print("Could not find message.")

def untrack_message(ts, channel):
    return find_tracked_message(ts, channel).delete_instance()