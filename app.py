from flask import Flask
from slackeventsapi import SlackEventAdapter
from dotenv import load_dotenv
import os
from utils.slackUtils import receive_message, receive_reaction
from utils.db import setup_db

setup_db()

load_dotenv()
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# This `app` represents your existing Flask app
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/events", app)

# Create an event listener for "reaction_added" events and print the emoji name
@slack_events_adapter.on('message')
def message(event):
    receive_message(event['event'])

@slack_events_adapter.on("reaction_added")
def reaction_added(event):
    receive_reaction(event['event'])


# Start the server on port 3000
if __name__ == "__main__":
    app.run(port=3000)
