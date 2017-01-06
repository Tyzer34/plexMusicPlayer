from flask_ask import audio, statement, question
from plexmusicplayer import ask, queue, app
from plexmusicplayer.utils import Track, QueueManager, MediaType
import plexmusicplayer.methods as methods

# --------------------------------------------------------------------------------------------
# Plex Music Requests - Intents

@ask.intent('PlexPlayTrackIntent')
def playTrack(track):
    speech, playlist = methods.processQuery(track, MediaType.Track)
    return makeRespone(speech, playlist)

@ask.intent('PlexPlayAlbumIntent')
def playAlbum(album):
    speech, playlist = methods.processQuery(album, MediaType.Album)
    return makeRespone(speech, playlist)

@ask.intent('PlexPlayTrackByArtistIntent')
def playTrack(track):
    speech, playlist = methods.processQuery(track, MediaType.Track)
    return makeRespone(speech, playlist)

@ask.intent('PlexPlayAlbumByArtistIntent')
def playAlbum(album):
    speech, playlist = methods.processQuery(album, MediaType.Album)
    return makeRespone(speech, playlist)

@ask.intent('PlexPlayArtistIntent')
def playArtist(artist):
    speech, playlist = methods.processQuery(artist, MediaType.Artist)
    return makeRespone(speech, playlist)

@ask.intent('PlexWhatSongIntent')
def whatSong():
    curTrack = queue.current
    if curTrack is None:
        speech = "The current song could not be requested at this moment."
    else:
        speech = "The song being played, is called " + curTrack.title + " by " + curTrack.artist + ", taken from the album " + curTrack.album + "."
    return statement(speech)

@ask.intent('PlexStatusIntent')
def status():
    return statement(queue.status)

def makeRespone(speech, playlist):
    if playlist != []:
        curTrack = queue.setQueue(playlist)
        return audio(speech).play(curTrack.stream_url)
    else:
        return statement(speech)