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
client_credentials_manager = SpotifyClientCredentials(
    client_id=cid, client_secret=secret
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
geniustoken = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(geniustoken)
clientmongo = pymongo.MongoClient(os.getenv("mongo_client"))
usersdb = clientmongo.Users
profilescol = usersdb.Profiles


def getsongnames(artistname):
    results = sp.search(q=f"artist:{artistname}", type="artist")
    items = results["artists"]["items"]
    if len(items) <= 0:
        return False
    artist = items[0]
    uri = artist["uri"]
    albums = sp.artist_albums(artist_id=uri)
    songnames = []
    for album in albums["items"]:
        if album["total_tracks"] == 1:
            if (
                "remix" not in album["name"].lower()
                and "acoustic" not in album["name"].lower()
                and "edit" not in album["name"].lower()
            ):
                songnames.append(album["name"])
        else:
            albumsongs = sp.album_tracks(album["uri"])
            songnames.extend(
                track["name"]
                for track in albumsongs["items"]
                if "remix" not in track["name"].lower()
                and "acoustic" not in track["name"].lower()
                and "edit" not in track["name"].lower()
            )
    return songnames


def searchartist(artistname):
    results = sp.search(q=f"artist:{artistname}", type="artist")
    items = results["artists"]["items"]
    if len(items) == 0:
        return False
    artist = items[0]
    return artist["name"]


def getlyrics(songname, artistname):
    return genius.search_song(songname, artistname)


def getrandomline(artistname):
    names = getsongnames(artistname)
    song = random.choice(names)
    lyrics = getlyrics(song, artistname)
    while lyrics is None:
        song = random.choice(names)
        lyrics = getlyrics(song, artistname)
    chorus = lyrics.lyrics
    chorus = chorus.split("\n")
    chorus = [x for x in chorus if x != ""]
    realchorus = [
        thelyric
        for thelyric in chorus
        if " " in thelyric
        and "embed" not in thelyric.lower()
        and "verse" not in thelyric.lower()
        and "chorus" not in thelyric.lower()
        and "bridge" not in thelyric.lower()
        and "refrain" not in thelyric.lower()
        and "outro" not in thelyric.lower()
        and "intro" not in thelyric.lower()
    ]
    line = random.choice(realchorus)
    return song, line


def getrandomalbumcover(artistname):
    results = sp.search(q=f"artist:{artistname}", type="artist")
    items = results["artists"]["items"]
    if len(items) <= 0:
        return False
    artist = items[0]
    uri = artist["uri"]
    albums = sp.artist_albums(artist_id=uri)
    albumcovers = []
    albumnames = []
    for album in albums["items"]:
        if album["images"][1]["url"] is not None:
            albumcovers.append(album["images"][1]["url"])
            albumnames.append(album["name"])
    albumcover = random.choice(albumcovers)
    index = albumcovers.index(albumcover)
    albumname = albumnames[index]
    return albumcover, albumname


def addcookie(key, value):
    session[key] = value


def delcookies():
    session.clear()


def getcookie(key):
    try:
        return x if ((x := session.get(key))) else False
    except:
        return False


def checkusernamealready(username):
    myquery = {"Username": username}
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
    document = [
        {
            "Username": username,
            "Password": passhash,
            "Created": str(datetime.datetime.now()),
            "Money": 0,
            "XP": 0,
            "SL": {},
            "AC": {},
        }
    ]
    profilescol.insert_many(document)
    return True


def gethashpass(username):
    myquery = {"Username": username}
    mydoc = profilescol.find(myquery)
    for x in mydoc:
        return x["Password"]
    return False


def getuser(username):
    myquery = {"Username": username}
    mydoc = profilescol.find(myquery)
    for x in mydoc:
        return x if x.get("Deleted", None) is None else False
    return False


def addmoney(username, amount):
    user = getuser(username)
    money = user["Money"]
    money = money + amount
    del user["Money"]
    user["Money"] = money
    profilescol.delete_one({"_id": user["_id"]})
    profilescol.insert_many([user])


def addxp(username, amount):
    user = getuser(username)
    money = user["XP"]
    money = money + amount
    del user["XP"]
    user["XP"] = money
    profilescol.delete_one({"_id": user["_id"]})
    profilescol.insert_many([user])


def changesonglyricscore(username, score, artist):
    user = getuser(username)
    songlyric = user["SL"]
    userscore = songlyric.get(artist.lower(), False)
    if userscore == False:
        _extracted_from_changesonglyricscore_6(score, songlyric, artist, user)
    elif score > userscore:
        del songlyric[artist.lower()]
        _extracted_from_changesonglyricscore_6(score, songlyric, artist, user)
    return True


# TODO Rename this here and in `changesonglyricscore`
def _extracted_from_changesonglyricscore_6(score, songlyric, artist, user):
    songlyric[artist.lower()] = score
    del user["SL"]
    user["SL"] = songlyric
    profilescol.delete_one({"_id": user["_id"]})
    profilescol.insert_many([user])


def changealbumcoverscore(username, score, artist):
    user = getuser(username)
    songlyric = user["AC"]
    userscore = songlyric.get(artist.lower(), False)
    if userscore == False:
        songlyric[artist.lower()] = score
        del user["AC"]
        user["AC"] = songlyric
        profilescol.delete_one({"_id": user["_id"]})
        profilescol.insert_many([user])
    else:
        if score > userscore:
            del songlyric[artist.lower()]
            songlyric[artist.lower()] = score
            del user["AC"]
            user["AC"] = songlyric
            profilescol.delete_one({"_id": user["_id"]})
            profilescol.insert_many([user])
    return True


def xpleaderboard():
    mydoc = profilescol.find().sort("XP", -1).limit(10)
    lb = []
    for x in mydoc:
        del x["Password"]
        lb.append(x)
    return lb


def moneyleaderboard():
    mydoc = profilescol.find().sort("Money", -1).limit(10)
    lb = []
    for x in mydoc:
        del x["Password"]
        lb.append(x)
    return lb


def getalbumnames(artistname):
    results = sp.search(q=f"artist:{artistname}", type="artist")
    items = results["artists"]["items"]
    if len(items) > 0:
        artist = items[0]
        uri = artist["uri"]
        albums = sp.artist_albums(artist_id=uri)
        return [
            album["name"].lower()
            for album in albums["items"]
            if album["images"][1]["url"] != None
        ]


def getalbumcover(albumname, artistname):
    results = sp.search(q=f"artist:{artistname}", type="artist")
    items = results["artists"]["items"]
    if len(items) > 0:
        artist = items[0]
        uri = artist["uri"]
        albums = sp.artist_albums(artist_id=uri)
        for album in albums["items"]:
            if (
                album["images"][1]["url"] != None
                and album["name"].lower() == albumname.lower()
            ):
                return album["images"][1]["url"]


def coverimagetobyte(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    buffer = BytesIO()
    img.save(buffer, format="png", quality=75)
    return buffer.getvalue()
