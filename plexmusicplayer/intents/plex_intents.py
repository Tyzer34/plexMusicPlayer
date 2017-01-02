from flask_ask import audio, statement
from plexmusicplayer import ask, queue, app
from plexmusicplayer.utils import Track, QueueManager, MediaType
import plexmusicplayer.methods as methods

# --------------------------------------------------------------------------------------------
# Plex Music Requests - Intents

@ask.intent('PlexPlayTrackIntent')
def playTrack(track):
    global queue
    speech, playlist = methods.processQuery(track, MediaType.Track)
    curTrack = queue.setQueue(playlist)
    return audio(speech).play(curTrack.stream_url)

@ask.intent('PlexPlayAlbumIntent')
def playAlbum(album):
    global queue
    speech, playlist = methods.processQuery(album, MediaType.Album)
    curTrack = queue.setQueue(playlist)
    return audio(speech).play(curTrack.stream_url)

@ask.intent('PlexPlayArtistIntent')
def playArtist(artist):
    global queue
    speech, playlist = methods.processQuery(artist, MediaType.Artist)
    curTrack = queue.setQueue(playlist)
    return audio(speech).play(curTrack.stream_url)

@ask.intent('PlexWhatSongIntent')
def whatSong():
    global queue
    curTrack = queue._current
    if curTrack:
        speech = "The song being played, is called " + curTrack.title + " by " + curTrack.artist + ", taken from the album " + curTrack.album + "."
    else:
        speech = "Sorry, there was a problem calling the current song."
    return statement(speech)