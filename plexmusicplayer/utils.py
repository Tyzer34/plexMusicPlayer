import collections
import random
from enum import Enum
import copy

# This QueueManager class is based on the following Flask-Ask example
# https://github.com/johnwheeler/flask-ask/blob/master/samples/audio/playlist_demo/playlist.py

class QueueManager(object):

    def __init__(self):
        self._urls = []
        self._queued = collections.deque()
        self._history = collections.deque()
        self._current = None

    @property
    def status(self):
        status = {
            'Current Position': self.current_position,
            'Current URl': self.current,
            'Next URL': self.up_next,
            'Previous': self.previous,
            'History': list(self.history)
        }
        return status

    @property
    def up_next(self):
        """Returns the url at the front of the queue"""
        qcopy = self._queued.copy()
        try:
            return qcopy.popleft()
        except IndexError:
            return None

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, url):
        self._save_to_history()
        self._current = url

    @property
    def history(self):
        return self._history

    @property
    def previous(self):
        history = self.history.copy()
        try:
            return history.pop()
        except IndexError:
            return None

    def add(self, url):
        self._urls.append(url)
        self._queued.append(url)

    def extend(self, urls):
        self._urls.extend(urls)
        self._queued.extend(urls)

    def _save_to_history(self):
        if self._current:
            self._history.append(self._current)

    def end_current(self):
        self._save_to_history()
        self._current = None

    def step(self):
        self.end_current()
        self._current = self._queued.popleft()
        return self._current

    def step_back(self):
        self._queued.appendleft(self._current)
        self._current = self._history.pop()
        return self._current

    def reset(self):
        self._queued = collections.deque(self._urls)
        self._history = []

    def start(self):
        return self.step()

    @property
    def current_position(self):
        return len(self._history) + 1

    def shuffle(self):
        shuffle = []
        for i in range(len(self._queued)):
            shuffle.append(self._queued.popleft())
        random.shuffle(shuffle)
        for track in shuffle:
            self._queued.appendleft(track)

    def setQueue(self, urls):
        self._urls = urls
        try:
            self._queued = collections.deque(urls)
            self.reset()
            return self.start()
        except IndexError:
            return None


class MediaType(Enum):
    Movie = '1'
    Show = '2'
    Season = '3'
    Episode = '4'
    Trailer = '5'
    Comic = '6'
    Person = '7'
    Artist = '8'
    Album = '9'
    Track = '10'


class Track(object):
    title = ""
    album = ""
    artist = ""
    stream_url = ""
    offset = 0

    def __init__(self, title, album, artist, stream_url):
        self.title = title
        self.album = album
        self.artist = artist
        self.stream_url = stream_url
        self.offset = 0

    def __repr__(self):
        return self.title

    def copy(self):
        return copy.deepcopy(self)

    def set_offset(self, offset):
        self.offset = offset