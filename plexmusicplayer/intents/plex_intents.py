from flask_ask import audio, statement
from plexmusicplayer import ask, queue
from plexmusicplayer.utils import MediaType
import plexmusicplayer.methods as methods


# --------------------------------------------------------------------------------------------
# Plex Music Requests - Intents
@ask.intent('PlexPlayTrackIntent')
def playTrack(track):
    speech, playlist = methods.processTrackQuery(track, MediaType.Track)
    return makeRespone(speech, playlist)


@ask.intent('PlexPlayTrackByArtistIntent')
def playTrackByArtist(track, artist):
    speech, playlist = methods.processTrackByArtistQuery(track, artist, MediaType.Track)
    return makeRespone(speech, playlist)

@ask.intent('PlexPlayAlbumIntent')
def playAlbum(album):
    speech, playlist = methods.processAlbumQuery(album, MediaType.Album)
    return makeRespone(speech, playlist)


@ask.intent('PlexPlayAlbumByArtistIntent')
def playAlbumByArtist(album, artist):
    speech, playlist = methods.processAlbumByArtistQuery(album, artist, MediaType.Album)
    return makeRespone(speech, playlist)


@ask.intent('PlexPlayArtistIntent')
def playArtist(artist):
    speech, playlist = methods.processArtistQuery(artist, MediaType.Artist)
    return makeRespone(speech, playlist)


@ask.intent('PlexPlayPlaylistIntent')
def playPlaylist(playlist_name):
    speech, playlist = methods.processPlaylistQuery(playlist_name, MediaType.Playlist)
    return makeRespone(speech, playlist)


@ask.intent('PlexQueueTrackIntent')
def queueTrack(track):
    speech, playlist = methods.processQueueTrackQuery(track, MediaType.Track)
    return makeQueueRespone(speech, playlist)


@ask.intent('PlexQueueTrackByArtistIntent')
def queueTrackByArtist(track, artist):
    speech, playlist = methods.processQueueTrackByArtistQuery(track, artist, MediaType.Track)
    return makeQueueRespone(speech, playlist)


@ask.intent('PlexQueueAlbumIntent')
def queueAlbum(album):
    speech, playlist = methods.processQueueAlbumQuery(album, MediaType.Album)
    return makeQueueRespone(speech, playlist)


@ask.intent('PlexQueueAlbumByArtistIntent')
def queueAlbumByArtist(album, artist):
    speech, playlist = methods.processQueueAlbumByArtistQuery(album, artist, MediaType.Album)
    return makeQueueRespone(speech, playlist)


@ask.intent('PlexQueueArtistIntent')
def queueArtist(artist):
    speech, playlist = methods.processQueueArtistQuery(artist, MediaType.Artist)
    return makeQueueRespone(speech, playlist)


@ask.intent('PlexQueuePlaylistIntent')
def queuePlaylist(playlist_name):
    speech, playlist = methods.processQueuePlaylistQuery(playlist_name, MediaType.Playlist)
    return makeQueueRespone(speech, playlist)


@ask.intent('PlexWhatSongIntent')
def whatSong():
    cur_track = queue.current
    if cur_track is None:
        speech = "The current song could not be requested at this moment."
    else:
        speech = "The song being played, is called " + cur_track.title + " by " + \
                 cur_track.artist + ", taken from the album " + cur_track.album + "."
    return statement(speech)


@ask.intent('PlexStatusIntent')
def status():
    return statement(queue.status)


def makeRespone(speech, playlist):
    if playlist:
        cur_track = queue.set_queue(playlist)
        return audio(speech).play(cur_track.stream_url)
    else:
        return statement(speech)


def makeQueueRespone(speech, playlist):
    if playlist:
        for track in playlist:
            queue.add(track)
    return statement(speech)

