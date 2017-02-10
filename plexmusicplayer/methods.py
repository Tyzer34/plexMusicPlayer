from .utils import Track
from difflib import SequenceMatcher
from os import environ
import requests
import xmltodict
import json
from fuzzywuzzy import process

stream_base_url = environ['PLEX_URL']
plex_token = "X-Plex-Token=" + environ['PLEX_TOKEN']
try:
    base_url = environ['PLEX_LOCAL_URL']
except:
    base_url = stream_base_url

num2words1 = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', \
            6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten', \
            11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', \
            15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen', 19: 'Nineteen'}
num2words2 = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']


# --------------------------------------------------------------------------------------------
# Plex Music Player - Methods
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def findAndConvertNumberInQuery(input):
    words = input.split()
    response = ""
    for word in  words:
        value = word
        if hasNumbers(word):
            number = int(word)
            value = numberToWords(number)
        response = response + value
    return response


def numberToWords(num):
    if 1 <= num < 19:
        return num2words1[num]
    elif 20 <= num <= 99:
        tens, below_ten = divmod(num, 10)
        return num2words2[tens - 2] + '-' + num2words1[below_ten]
    else:
        return str(num)


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def getStreamUrl(sub_url):
    return stream_base_url + sub_url + "?download=1&" + plex_token


def getLookupUrl(sub_url):
    plex_url = base_url + sub_url + "?" + plex_token
    return plex_url


def getJsonFromPlex(url):
    response = requests.get(url)
    xml_obj = xmltodict.parse(response.text)
    json_obj = json.loads(json.dumps(xml_obj))
    return json_obj


def parseTrackJson(json_obj):

    directory = json_obj['MediaContainer']['Track']
    if isinstance(directory, list):
        server = directory[0]['@sourceTitle']
        title = directory[0]['@title']
        album = directory[0]['@parentTitle']
        artist = directory[0]['@grandparentTitle']
        sub_url = directory[0]['Media']['Part']['@key']
    else:
        server = directory['@sourceTitle']
        title = directory['@title']
        album = directory['@parentTitle']
        artist = directory['@grandparentTitle']
        sub_url = directory['Media']['Part']['@key']
    
    stream_url = getStreamUrl(sub_url)
    return Track(title, album, artist, stream_url), server


def parseTrackByArtistJson(json_obj, artist):

    directory = json_obj['MediaContainer']['Track']
    if isinstance(directory, list):
        server = None
        title = None
        album = None
        sub_url = None
        for item in directory:
            if similar(item['@grandparentTitle'], artist) > 0.5:
                server = item['@sourceTitle']
                title = item['@title']
                album = item['@parentTitle']
                artist = item['@grandparentTitle']
                sub_url = item['Media']['Part']['@key']
                break
    else:
        server = directory['@sourceTitle']
        title = directory['@title']
        album = directory['@parentTitle']
        artist = directory['@grandparentTitle']
        sub_url = directory['Media']['Part']['@key']

    stream_url = getStreamUrl(sub_url)
    return Track(title, album, artist, stream_url), server


def parseAlbumJson(json_obj):

    playlist = []
    directory = json_obj['MediaContainer']['Directory']
    if isinstance(directory, list):
        album = directory[0]['@title']
        artist = directory[0]['@parentTitle']
        server = directory[0]['@sourceTitle']
        sub_url = directory[0]['@key']
    else:        
        album = directory['@title']
        artist = directory['@parentTitle']
        server = directory['@sourceTitle']
        sub_url = directory['@key']
   
    album_url = getLookupUrl(sub_url)
    json_album = getJsonFromPlex(album_url)
    if '@title' in json_album['MediaContainer']['Track']:
        json_album['MediaContainer']['Track'] = [json_album['MediaContainer']['Track']]

    playlist = createAlbumPlaylist(json_album['MediaContainer']['Track'], album, artist)
    return album, artist, server, playlist


def parseAlbumByArtistJson(json_obj, artist):

    directory = json_obj['MediaContainer']['Directory']
    if isinstance(directory, list):
        server = None
        album = None
        sub_url = None
        for item in directory:
            if similar(item['@parentTitle'], artist) > 0.5:
                album = item['@title']
                artist = item['@parentTitle']
                server = item['@sourceTitle']
                sub_url = item['@key']
                break
    else:
        album = directory['@title']
        artist = directory['@parentTitle']
        server = directory['@sourceTitle']
        sub_url = directory['@key']

    album_url = getLookupUrl(sub_url)
    json_album = getJsonFromPlex(album_url)
    if '@title' in json_album['MediaContainer']['Track']:
        json_album['MediaContainer']['Track'] = [json_album['MediaContainer']['Track']]

    playlist = createAlbumPlaylist(json_album['MediaContainer']['Track'], album, artist)
    return album, artist, server, playlist


def parseArtistJson(json_obj):
    playlist = []

    directory = json_obj['MediaContainer']['Directory']
    if isinstance(directory, list):
        artist = directory[0]['@title']
        server = directory[0]['@sourceTitle']
        sub_url = directory[0]['@key']
    else:    
        artist = directory['@title']
        server = directory['@sourceTitle']
        sub_url = directory['@key']
    
    artist_url = getLookupUrl(sub_url)
    json_artist = getJsonFromPlex(artist_url)
    if '@title' in json_artist['MediaContainer']['Directory']:
        json_artist['MediaContainer']['Directory'] = [json_artist['MediaContainer']['Directory']]
    for alb in json_artist['MediaContainer']['Directory']:
        album = alb['@title']
        sub_url = alb['@key']
        album_url = getLookupUrl(sub_url)
        json_album = getJsonFromPlex(album_url)
        if '@title' in json_album['MediaContainer']['Track']:
            json_album['MediaContainer']['Track'] = [json_album['MediaContainer']['Track']]

        playlist += createAlbumPlaylist(json_album['MediaContainer']['Track'], album, artist)
    return artist, server, playlist


def parsePlaylistJson(json_obj):
    directory = json_obj['MediaContainer']['Playlist']
    if isinstance(directory, list):
        playlist_name = directory[0]['@title']
        server = directory[0]['@sourceTitle']
        sub_url = directory[0]['@key']
    else:
        playlist_name = directory['@title']
        server = directory['@sourceTitle']
        sub_url = directory['@key']
    playlist_url = getLookupUrl(sub_url)
    json_playlist = getJsonFromPlex(playlist_url)
    playlist = createPlaylistPlaylist(json_playlist)
    return playlist_name, server, playlist


def createPlaylistPlaylist(json_playlist):
    playlist = []
    for track in json_playlist['MediaContainer']['Track']:
        title = track['@title']
        sub_url = track['Media']['Part']['@key']
        artist = track['@grandparentTitle']
        album = track['@parentTitle']
        stream_url = getStreamUrl(sub_url)
        playlist.append(Track(title, album, artist, stream_url))
    return playlist


def createAlbumPlaylist(json_album, album, artist):
    playlist = []

    for track in json_album:
        title = track['@title']
        sub_url = track['Media']['Part']['@key']
        stream_url = getStreamUrl(sub_url)
        playlist.append(Track(title, album, artist, stream_url))
    return playlist


def callPlex(query, mediaType):

    searchQueryUrl = base_url + "/search?query=" + query + "&" + plex_token + "&type=" + mediaType.value

    return getJsonFromPlex(searchQueryUrl)


def processQuery(query, mediaType):
    json_obj = callPlex(query, mediaType)
    if json_obj['MediaContainer']['@size'] == '0':
        # are there numbers that need to be converted?
        if hasNumbers(query):
            json_obj = callPlex(findAndConvertNumberInQuery(query), mediaType)
    if json_obj['MediaContainer']['@size'] == '0' and mediaType.value in ['8', '9']:
        # fuzzy match on albums and artists
        query = fuzzy_match(query, mediaType)
        if query:
            json_obj = callPlex(query, mediaType)
    if json_obj['MediaContainer']['@size'] == '0':
        raise LookupError("No results could be found")
    return json_obj


def fuzzy_match(query, media_type):
    dirs = get_music_directories()
    names = get_names_by_first_letter(dirs, query[0].upper(), media_type)
    if query.lower().startswith('the '):
        # dropping 'the ' off of queries where it might have been mistakenly added
        # (i.e. play the red house painters > red house painters)
        # the reverse is already handled by plex not sorting on the, los, la, etc...
        # (i.e. play head and the heart > the head and the heart)
        names.extend(get_names_by_first_letter(dirs, query[4].upper(), media_type))
    best_match = process.extractOne(query, names)
    return best_match[0] if best_match and best_match[1] > 60 else None


def get_music_directories():
    url = "{0}/library/sections/?{1}".format(base_url, plex_token)
    directories = getJsonFromPlex(url)['MediaContainer']['Directory']
    return [directory['@key'] for directory in directories if directory and directory['@type'] == 'artist']


def get_names_by_first_letter(dirs, letter, media_type):
    names = []
    for dir in dirs:
        url = "{0}/library/sections/{1}/firstCharacter/{2}?{3}&type={4}".format(
            base_url, dir, letter, plex_token, media_type.value)
        results = getJsonFromPlex(url)['MediaContainer']['Directory']
        names.extend([result['@title'] for result in results])
    return names


def processTrackQuery(track, mediaType):
    playlist = []
    try:
        track, server = parseTrackJson(processQuery(track, mediaType))
        speech = "Playing " + track.title + " by " + track.artist + " from " + server + "."
        playlist.append(track)
        return speech, playlist
    except:
        speech = "I was not able to find " + track + " in your library."
        return speech, []


def processTrackByArtistQuery(track, artist, mediaType):
    playlist = []
    try:
        track, server = parseTrackByArtistJson(processQuery(track, mediaType), artist)
        speech = "Playing " + track.title + " by " + track.artist + " from " + server + "."
        playlist.append(track)
        return speech, playlist
    except:
        speech = "I was not able to find " + track + " by " + artist + " in your library."
        return speech, []


def processAlbumQuery(album, mediaType):
    try:
        album, artist, server, playlist = parseAlbumJson(processQuery(album, mediaType))
        speech = "Playing " + album + " by " + artist + " from " + server + "."
        return speech, playlist
    except:
        speech = "I was not able to find " + album + " in your library."
        return speech, []


def processAlbumByArtistQuery(album, artist, mediaType):
    try:
        album, artist, server, playlist = parseAlbumByArtistJson(processQuery(album, mediaType), artist)
        speech = "Playing " + album + " by " + artist + " from " + server + "."
        return speech, playlist
    except:
        speech = "I was not able to find " + album + " by " + artist + " in your library."
        return speech, []


def processArtistQuery(artist, mediaType):
    try:
        artist, server, playlist = parseArtistJson(processQuery(artist, mediaType))
        speech = "Playing " + artist + " from " + server + "."
        return speech, playlist
    except:
        speech = "I was not able to find " + artist + " in your library."
        return speech, []


def processPlaylistQuery(playlist_name, mediaType):
    try:
        artist, server, playlist = parsePlaylistJson(processQuery(playlist_name, mediaType))
        speech = "Playing playlist " + playlist_name + " from " + server + "."
        return speech, playlist
    except:
        speech = "I was not able to find " + playlist_name + " in your library."
        return speech, []


def processQueueTrackQuery(track, mediaType):
    playlist = []
    try:
        track, server = parseTrackJson(processQuery(track, mediaType))
        speech = "Added " + track.title + " by " + track.artist + " to queue."
        playlist.append(track)
        return speech, playlist
    except:
        speech = "I was not able to find " + track + " in your library."
        return speech, []


def processQueueTrackByArtistQuery(track, artist, mediaType):
    playlist = []
    try:
        track, server = parseTrackByArtistJson(processQuery(track, mediaType), artist)
        speech = "Added " + track.title + " by " + track.artist + " to queue."
        playlist.append(track)
        return speech, playlist
    except:
        speech = "I was not able to find " + track + " by " + artist + " in your library."
        return speech, []


def processQueueAlbumQuery(album, mediaType):
    try:
        album, artist, server, playlist = parseAlbumJson(processQuery(album, mediaType))
        speech = "Added " + album + " by " + artist + " to queue."
        return speech, playlist
    except:
        speech = "I was not able to find " + album + " in your library."
        return speech, []


def processQueueAlbumByArtistQuery(album, artist, mediaType):
    try:
        album, artist, server, playlist = parseAlbumByArtistJson(processQuery(album, mediaType), artist)
        speech = "Added " + album + " by " + artist + " to queue."
        return speech, playlist
    except:
        speech = "I was not able to find " + album + " by " + artist + " in your library."
        return speech, []


def processQueueArtistQuery(artist, mediaType):
    try:
        artist, server, playlist = parseArtistJson(processQuery(artist, mediaType))
        speech = "Added " + artist + " to queue."
        return speech, playlist
    except:
        speech = "I was not able to find " + artist + " in your library."
        return speech, []


def processQueuePlaylistQuery(playlist_name, mediaType):
    try:
        playlist_name, server, playlist = parsePlaylistJson(processQuery(playlist_name, mediaType))
        speech = "Added playlist " + playlist_name + " to queue."
        return speech, playlist
    except:
        speech = "I was not able to find " + playlist_name + " in your library."
        return speech, []
