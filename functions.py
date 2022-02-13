import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import random
from flask import session
from string import printable
from html import escape as esc
import pymongo
import dns

cid = os.getenv("SPOTIPY_CLIENT_ID")
secret = os.getenv("SPOTIPY_CLIENT_SECRET")
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
geniustoken = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(geniustoken)
clientmongo = pymongo.MongoClient(os.getenv("mongo_client"))
usersdb = clientmongo.Users
profilescol = usersdb.Profiles

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

def makeaccount(username, password, passwordagain):
  if len(username) > 25:
    return "Your username cannot have more than 25 letters!"
  if len(username) < 2:
    return "You have to have more than 2 letters in your username!"
  if set(username).difference(printable) or esc(username) != username:
    return "Your username cannot contain any special characters!"
  if username != username.lower():
    return "Your username has to be all lowercase!"
  if checkusernamealready(username) == True:
    return "A user already has this username! Try another one."
  if password != passwordagain:
    return "The two passwords don't match!"
  if len(password) > 25:
    return "Your password cannot have more than 25 letters!"
  if len(password) < 2:
    return "You have to have more than 2 letters in your password!"
  if set(password).difference(printable):
    return "Your password cannot contain any special characters!"
  passhash = generate_password_hash(password)
  document = [{
    "Username": username,
    "Password": passhash,
    "Created": str(datetime.datetime.now()),
    "Money": 0,
    "XP": 0
  }]
  profilescol.insert_many(document)
  return True