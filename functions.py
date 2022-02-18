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
import datetime
from PIL import Image
import requests
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash

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
        if "remix" not in album['name'].lower() and "acoustic" not in album['name'].lower() and "edit" not in album['name'].lower():
          songnames.append(album['name'])
      else:
        albumsongs = sp.album_tracks(album['uri'])
        for track in albumsongs['items']:
          if "remix" not in track['name'].lower() and "acoustic" not in track['name'].lower() and "edit" not in track['name'].lower():
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
  chorus = lyrics.lyrics
  # lyrics = lyrics.lyrics
  # parts = lyrics.split("[")
  # chorustrue = False
  # for part in parts:
  #   if "Chorus]" in part:
  #     chorustrue = part
  # while chorustrue == False:
  #   song = random.choice(names)
  #   lyrics = getlyrics(song, artistname)
  #   while lyrics == None:
  #     song = random.choice(names)
  #     lyrics = getlyrics(song, artistname)
  #   lyrics = lyrics.lyrics
  #   parts = lyrics.split("[")
  #   chorustrue = False
  #   for part in parts:
  #     if "Chorus]" in part:
  #       chorustrue = part
  # chorus = chorustrue.replace("Chorus]", "")
  chorus = chorus.split("\n")
  chorus = [ x for x in chorus if x != ""]
  realchorus = []
  for thelyric in chorus:
    if " " in thelyric:
      if "embed" not in thelyric.lower() and "verse" not in thelyric.lower() and "chorus" not in thelyric.lower() and "bridge" not in thelyric.lower():
        realchorus.append(thelyric)
  line = random.choice(realchorus)
  return song, line

def getrandomalbumcover(artistname):
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

def checkusernamealready(username):
  myquery = { "Username": username }
  mydoc = profilescol.find(myquery)
  for x in mydoc:
    return True
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
    "XP": 0,
    "SL": {},
    "AC": {}
  }]
  profilescol.insert_many(document)
  return True

def gethashpass(username):
  myquery = { "Username": username }
  mydoc = profilescol.find(myquery)
  for x in mydoc:
    return x['Password']
  return False

def getuser(username):
  myquery = { "Username": username }
  mydoc = profilescol.find(myquery)
  for x in mydoc:
    if x.get("Deleted", None) == None:
      return x
    return False
  return False

def addmoney(username, amount):
  user = getuser(username)
  money = user['Money']
  money = money + amount
  del user['Money']
  user['Money'] = money
  profilescol.delete_one({"_id": user['_id']})
  profilescol.insert_many([user])

def addxp(username, amount):
  user = getuser(username)
  money = user['XP']
  money = money + amount
  del user['XP']
  user['XP'] = money
  profilescol.delete_one({"_id": user['_id']})
  profilescol.insert_many([user])

def changesonglyricscore(username, score, artist):
  user = getuser(username)
  songlyric = user['SL']
  userscore = songlyric.get(artist.lower(), False)
  if userscore == False:
    songlyric[artist.lower()] = score
    del user['SL']
    user['SL'] = songlyric
    profilescol.delete_one({"_id": user['_id']})
    profilescol.insert_many([user])
  else:
    if score > userscore:
      del songlyric[artist.lower()]
      songlyric[artist.lower()] = score
      del user['SL']
      user['SL'] = songlyric
      profilescol.delete_one({"_id": user['_id']})
      profilescol.insert_many([user])
  return True

def changealbumcoverscore(username, score, artist):
  user = getuser(username)
  songlyric = user['AC']
  userscore = songlyric.get(artist.lower(), False)
  if userscore == False:
    songlyric[artist.lower()] = score
    del user['AC']
    user['AC'] = songlyric
    profilescol.delete_one({"_id": user['_id']})
    profilescol.insert_many([user])
  else:
    if score > userscore:
      del songlyric[artist.lower()]
      songlyric[artist.lower()] = score
      del user['AC']
      user['AC'] = songlyric
      profilescol.delete_one({"_id": user['_id']})
      profilescol.insert_many([user])
  return True

def xpleaderboard():
  mydoc = profilescol.find().sort("XP", -1).limit(10)
  lb = []
  for x in mydoc:
    del x['Password']
    lb.append(x)
  return lb

def moneyleaderboard():
  mydoc = profilescol.find().sort("Money", -1).limit(10)
  lb = []
  for x in mydoc:
    del x['Password']
    lb.append(x)
  return lb

def getalbumnames(artistname):
  results = sp.search(q='artist:' + artistname, type='artist')
  albumnames = []
  items = results['artists']['items']
  if len(items) > 0:
    artist = items[0]
    uri = artist['uri']
    albums = sp.artist_albums(artist_id=uri)
    for album in albums['items']:
      if album['images'][1]['url'] != None:
        albumnames.append(album['name'].lower())
    return albumnames

def getalbumcover(albumname, artistname):
  results = sp.search(q='artist:' + artistname, type='artist')
  items = results['artists']['items']
  if len(items) > 0:
    artist = items[0]
    uri = artist['uri']
    albums = sp.artist_albums(artist_id=uri)
    for album in albums['items']:
      if album['images'][1]['url'] != None:
        if album['name'].lower() == albumname.lower():
          return album['images'][1]['url']

def coverimagetobyte(url):
  response = requests.get(url)
  img = Image.open(BytesIO(response.content))
  buffer = BytesIO()
  img.save(buffer, format='png', quality=75)
  byte_im = buffer.getvalue()
  return byte_im