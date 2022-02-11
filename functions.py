import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import random
from flask import session

cid = os.getenv("SPOTIPY_CLIENT_ID")
secret = os.getenv("SPOTIPY_CLIENT_SECRET")
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
geniustoken = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(geniustoken)

def getsongnames(artistname):
  results = sp.search(q='artist:' + artistname, type='artist')
  songnames = []
  items = results['artists']['items']
  if len(items) > 0:
    artist = items[0]
    uri = artist['uri']
    albums = sp.artist_albums(artist_id=uri)
    for album in albums['items']:
      if album['total_tracks'] == 1:
        if "remix" not in album['name'].lower() and "acoustic" not in album['name'].lower():
          songnames.append(album['name'])
      else:
        albumsongs = sp.album_tracks(album['uri'])
        for track in albumsongs['items']:
          if "remix" not in track['name'].lower() and "acoustic" not in track['name'].lower():
            songnames.append(track['name'])
    return songnames
  else:
    return False

def getlyrics(songname, artistname):
  song = genius.search_song(songname, artistname)
  return song

def getrandomline(artistname):
  names = getsongnames(artistname)
  song = random.choice(names)
  lyrics = getlyrics(song, artistname)
  while lyrics == None:
    song = random.choice(names)
    lyrics = getlyrics(song, artistname)
  lyrics = lyrics.lyrics
  parts = lyrics.split("[")
  chorustrue = False
  for part in parts:
    if "Chorus]" in part:
      chorustrue = part
  while chorustrue == False:
    song = random.choice(names)
    lyrics = getlyrics(song, artistname)
    while lyrics == None:
      song = random.choice(names)
      lyrics = getlyrics(song, artistname)
    lyrics = lyrics.lyrics
    parts = lyrics.split("[")
    chorustrue = False
    for part in parts:
      if "Chorus]" in part:
        chorustrue = part
  chorus = chorustrue.replace("Chorus]", "")
  chorus = chorus.split("\n")
  chorus = [ x for x in chorus if x != ""]
  line = random.choice(chorus)
  return song, line

def getalbumcovers(artistname):
  results = sp.search(q='artist:' + artistname, type='artist')
  albumcovers = []
  albumnames = []
  items = results['artists']['items']
  if len(items) > 0:
    artist = items[0]
    uri = artist['uri']
    albums = sp.artist_albums(artist_id=uri)
    for album in albums['items']:
      if album['images'][1]['url'] != None:
        albumcovers.append(album['images'][1]['url'])
        albumnames.append(album['name'])
    albumcover = random.choice(albumcovers)
    index = albumcovers.index(albumcover)
    albumname = albumnames[index]
    return albumcover, albumname
  else:
    return False

print(getalbumcovers("nico collins"))

def addcookie(key, value):
  session[key] = value

def delcookies():
  session.clear()

def getcookie(key):
  try:
    if (x := session.get(key)):
      return x
    else:
      return False
  except:
    return False