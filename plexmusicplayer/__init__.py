from flask import Flask
from flask_ask import Ask
from plexmusicplayer.utils import QueueManager

# --------------------------------------------------------------------------------------------
# INITIALISATION

app = Flask(__name__)
ask = Ask(app, "/plex")

queue = QueueManager()

import plexmusicplayer.methods
import plexmusicplayer.intents
