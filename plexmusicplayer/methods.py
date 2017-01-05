from .utils import Track, QueueManager, MediaType
from os import environ
import requests
import xmltodict
import json

base_url = environ['PLEX_URL']
plex_token = "X-Plex-Token=" + environ['PLEX_TOKEN']

# --------------------------------------------------------------------------------------------
# Plex Music Player - Methods

def getStreamUrl(sub_url):
    global base_url, plex_token
    return base_url + sub_url + "?download=1&" + plex_token

def getLookupUrl(sub_url):
    global base_url, plex_token
    plex_url = base_url + sub_url + "?" + plex_token
    return plex_url

def getJsonFromPlex(url):
    response = requests.get(url)
    xml_obj = xmltodict.parse(response.text)
    json_obj = json.loads(json.dumps(xml_obj))
    return json_obj

def parseTrackJson(json_obj):
    print('parseTrackJson')

    directory = json_obj['MediaContainer']['Track']
    if isinstance(directory, list):
        server = json_obj['MediaContainer']['Track'][0]['@sourceTitle']
        print(server)
        title = json_obj['MediaContainer']['Track'][0]['@title']
        print(title)
        album = json_obj['MediaContainer']['Track'][0]['@parentTitle']
        print(album)
        artist = json_obj['MediaContainer']['Track'][0]['@originalTitle']
        print(artist)
        sub_url = json_obj['MediaContainer']['Track'][0]['Media']['Part']['@key']
        print(sub_url)
    else:    
        print('not a list')
        server = json_obj['MediaContainer']['Track']['@sourceTitle']
        title = json_obj['MediaContainer']['Track']['@title']
        album = json_obj['MediaContainer']['Track']['@parentTitle']
        artist = json_obj['MediaContainer']['Track']['@originalTitle']
        sub_url = json_obj['MediaContainer']['Track']['Media']['Part']['@key']
    
    print(sub_url)
    stream_url = getStreamUrl(sub_url)
    return Track(title, album, artist, stream_url), server

def parseAlbumJson(json_obj):
    print('parseAlbumJson')
    
    playlist = []
    directory = json_obj['MediaContainer']['Directory']
    if isinstance(directory, list):
        album = json_obj['MediaContainer']['Directory'][0]['@title']
        artist = json_obj['MediaContainer']['Directory'][0]['@parentTitle']
        server = json_obj['MediaContainer']['Directory'][0]['@sourceTitle']
        sub_url = json_obj['MediaContainer']['Directory'][0]['@key']
    else:        
        album = json_obj['MediaContainer']['Directory']['@title']
        artist = json_obj['MediaContainer']['Directory']['@parentTitle']
        server = json_obj['MediaContainer']['Directory']['@sourceTitle']
        sub_url = json_obj['MediaContainer']['Directory']['@key']
   
    album_url = getLookupUrl(sub_url)
    json_album = getJsonFromPlex(album_url)
    if '@title' in json_album['MediaContainer']['Track']:
        json_album['MediaContainer']['Track'] = [json_album['MediaContainer']['Track']]
    for track in json_album['MediaContainer']['Track']:
        title = track['@title']
        sub_url = track['Media']['Part']['@key']
        stream_url = getStreamUrl(sub_url)
        playlist.append(Track(title, album, artist, stream_url))
    return album, artist, server, playlist

def parseArtistJson(json_obj):
    print('parseArtistJson')
    playlist = []

    directory = json_obj['MediaContainer']['Directory']
    if isinstance(directory, list):
        artist = json_obj['MediaContainer']['Directory'][0]['@title']
        server = json_obj['MediaContainer']['Directory'][0]['@sourceTitle']
        sub_url = json_obj['MediaContainer']['Directory'][0]['@key']
    else:    
        artist = json_obj['MediaContainer']['Directory']['@title']
        server = json_obj['MediaContainer']['Directory']['@sourceTitle']
        sub_url = json_obj['MediaContainer']['Directory']['@key']
    
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
        for track in json_album['MediaContainer']['Track']:
            title = track['@title']
            sub_url = track['Media']['Part']['@key']
            stream_url = getStreamUrl(sub_url)
            playlist.append(Track(title, album, artist, stream_url))
    return artist, server, playlist

def processQuery(query, mediaType):
    global base_url, plex_token
    searchQueryUrl = base_url + "/search?query=" + query + "&" + plex_token + "&type=" + mediaType.value
    json_obj = getJsonFromPlex(searchQueryUrl)
    playlist = []
    try:
        if (mediaType == MediaType.Track):
            track, server = parseTrackJson(json_obj)
            speech = "Playing " + track.title + " by " + track.artist + " from " + server + "."
            playlist.append(track)
        elif (mediaType == MediaType.Album):
            album, artist, server, playlist = parseAlbumJson(json_obj)
            speech = "Playing " + album + " by " + artist + " from " + server + "."
        elif (mediaType == MediaType.Artist):
            artist, server, playlist = parseArtistJson(json_obj)
            speech = "Playing " + artist + " from " + server + "."
        return speech, playlist
    except:
        speech = "I was not able to find " + query + " in your library."
        return speech, []