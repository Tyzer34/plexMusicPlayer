from multiprocessing import Value
import random
from enum import Enum
import copy


# This QueueManager class is based on the following Flask-Ask example
# https://github.com/johnwheeler/flask-ask/blob/master/samples/audio/playlist_demo/playlist.py
class QueueManager(object):

    def __init__(self):
        self._playlist = []
        self._counter = Value('i', 0)

    @property
    def status(self):
        playlist_count = len(self._playlist)
        status = 'Current Queue Status: Songs in Queue ' + str(playlist_count) + \
                 ' | Current Song is ' + str(self.current) + " | Songs left to Play are: "
        for i in range(self._counter.value + 1, len(self._playlist)):
            status += str(self._playlist[i]) + ', '
        return status

    @property
    def whats_next(self):
        if self._counter.value < len(self._playlist) - 1:
            return self._playlist[self._counter.value + 1]
        else:
            return None

    @property
    def current(self):
        with self._counter.get_lock():
            return self._playlist[self._counter.value]

    @property
    def whats_prev(self):
        if self._counter.value > 0:
            return self._playlist[self._counter.value - 1]
        else:
            return None

    def add(self, url):
        self._playlist.append(url)

    def go_next(self):
        with self._counter.get_lock():
            self._counter.value += 1
        return self._playlist[self._counter.value]

    def go_prev(self):
        with self._counter.get_lock():
            self._counter.value -= 1
        return self._playlist[self._counter.value]

    def reset(self):
        with self._counter.get_lock():
            self._counter.value = 0

    @property
    def current_position(self):
        return self._counter.value

    def shuffle(self):
        shuffle = self._playlist[(self._counter.value+1):]
        random.shuffle(shuffle)
        self._playlist = self._playlist[:(self._counter.value+1)] + shuffle

    def set_queue(self, urls):
        self.reset()
        del self._playlist
        self._playlist = []
        self._playlist.extend(urls)
        return self.current


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
    Playlist = '15'


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
