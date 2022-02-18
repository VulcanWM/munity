from flask import Flask, render_template, request, redirect, send_file
from functions import getrandomline, addcookie, delcookies, getcookie, makeaccount, gethashpass, getuser, addmoney, addxp, changesonglyricscore, xpleaderboard, moneyleaderboard, changealbumcoverscore, getrandomalbumcover, getalbumnames, coverimagetobyte, getalbumcover
import os
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

@app.route("/")
def index():
  return render_template("index.html", artist=getcookie("artist"), username=getcookie("User"))

@app.route("/setartist", methods=['POST', 'GET'])
def getartistfunc():
  if request.method == 'POST':
    name = request.form['artist']
    username = getcookie("User")
    delcookies()
    addcookie("artist", name)
    if username != False:
      addcookie("User", username)
    return redirect("/")
  else:
    return render_template("setartist.html", artist=getcookie("artist"), username=getcookie("User"))

@app.route("/guesssong", methods=['POST', 'GET'])
def guessartistfunc():
  if request.method == 'POST':
    song = request.form['song']
    if getcookie("song") == False:
      return redirect("/guesssong")
    name = getcookie("artist")
    accsong = getcookie("song")
    songnumber = getcookie("songnumber")
    points = getcookie("points")
    username = getcookie("User")
    delcookies()
    if username != False:
      addcookie("User", username)
    if song.lower() == accsong.lower():
      points = points + 1
      addcookie("artist", name)
      if songnumber > 19:
        if username != False:
          addxp(username, points*3)
          addmoney(username, points*3)
          changesonglyricscore(username, points*5, name.lower())
        return render_template("guesssongresults.html", result=True, end=points*5, artist=getcookie("artist"), username=getcookie("User"))
      addcookie("songnumber", songnumber)
      addcookie("points", points)
      return render_template("guesssongresults.html", result=True, end=False, artist=getcookie("artist"), username=getcookie("User"))
    else:
      addcookie("artist", name)
      if songnumber > 19:
        if username != False:
          addxp(username, points)
          addmoney(username, points)
          changesonglyricscore(username, points*5, name.lower())
        return render_template("guesssongresults.html", result=accsong, end=points*5, artist=getcookie("artist"), username=getcookie("User"))
      addcookie("songnumber", songnumber)
      addcookie("points", points)
      return render_template("guesssongresults.html", result=accsong, end=False, artist=getcookie("artist"), username=getcookie("User"))
  else:
    name = getcookie("artist")
    songnumber = getcookie("songnumber")
    if songnumber == False:
      songnumber = 0
    points = getcookie("points")
    if points == False:
      points = 0
    if name == False:
      return redirect("/")
    func = getrandomline(name)
    username = getcookie("User")
    delcookies()
    if username != False:
      addcookie("User", username)
    addcookie("song", func[0])
    addcookie("artist", name)
    addcookie("songnumber", songnumber+1)
    addcookie("points", points)
    return render_template("guesssong.html", lyric=func[1], artist=name, songnumber=songnumber+1, points=points, username=getcookie("User"))

@app.route("/sticky.js")
def scriptjs():
  return send_file("static/sticky.js")

@app.route('/main.css')
def maincss():
  return send_file("static/main.css")

@app.route("/signup")
def signuppage():
  if getcookie("User") == False:
    return render_template("signup.html", artist=getcookie("artist"))
  else:
    return redirect("/")
  
@app.route("/signup", methods=['POST', 'GET'])
def signupfunc():
  if request.method == 'POST':
    if getcookie("User") != False:
      return redirect("/")
    username = request.form['username']
    password = request.form['password']
    passwordagain = request.form['passwordagain']
    func = makeaccount(username, password, passwordagain)
    if func == True:
      addcookie("User", username)
      return redirect("/")
    else:
      return render_template("signup.html", error=func, artist=getcookie("artist"))

@app.route("/logout")
def logout():
  name = getcookie("artist")
  songnumber = getcookie("songnumber")
  points = getcookie("points")
  delcookies()
  if name != False:
    addcookie("artist", name)
  if songnumber != False:
    addcookie("songnumber", songnumber)
  if points != False:
    addcookie("points", points)
  return redirect("/")

@app.route("/login")
def loginpage():
  if getcookie("User") == False:
    return render_template("login.html", artist=getcookie("artist"))
  else:
    return redirect("/")

@app.route("/login", methods=['POST', 'GET'])
def loginfunc():
  if request.method == 'POST':
    if getcookie("User") != False:
      return render_template("login.html", error="You have already logged in!", artist=getcookie("artist"))
    username = request.form['username']
    if getuser(username) == False:
      return render_template("login.html", error="That is not a username!", artist=getcookie("artist"))
    password = request.form['password']
    if check_password_hash(gethashpass(username), password) == False:
      return render_template("login.html", error="Wrong password!", artist=getcookie("artist"))
    addcookie("User", username)
    return redirect("/")
  else:
    return redirect("/")

@app.route('/profile')
def profile():
  if getcookie("User") == False:
    return redirect("/")
  else:
    return render_template("profile.html", user=getuser(getcookie("User")), artist=getcookie("artist"), username=getcookie("User"))

@app.route("/@<username>")
def userprofile(username):
  if getuser(username) == False:
    return redirect("/")
  if getcookie("User") != False:
    if getcookie("User") == username:
      return redirect("/profile")
  return render_template("userprofile.html", user=getuser(username), artist=getcookie("artist"), username=getcookie("User"))

@app.route("/lb")
@app.route("/leaderboard")
def leaderboardpage():
  xplb = xpleaderboard()
  moneylb = moneyleaderboard()
  if getcookie("User") == False:
    return render_template("leaderboard.html", xplb=xplb, moneylb=moneylb, logged=False)
  else:
    return render_template("leaderboard.html", xplb=xplb, moneylb=moneylb, logged=getcookie("User"), artist=getcookie("artist"))

@app.route("/guessalbum", methods=['POST', 'GET'])
def guessalbum():
  if request.method == 'POST':
    song = request.form['song']
    if getcookie("album") == False:
      return redirect("/guessalbum")
    name = getcookie("artist")
    accsong = getcookie("album")
    songnumber = getcookie("albumnumber")
    points = getcookie("points2")
    username = getcookie("User")
    delcookies()
    if username != False:
      addcookie("User", username)
    if song.lower() == accsong.lower():
      points = points + 1
      addcookie("artist", name)
      if songnumber > 9:
        if username != False:
          addxp(username, points)
          addmoney(username, points)
          changealbumcoverscore(username, points*10, name.lower())
        return render_template("guessalbumresults.html", result=True, end=points*10, artist=getcookie("artist"), username=getcookie("User"))
      addcookie("albumnumber", songnumber)
      addcookie("points2", points)
      return render_template("guessalbumresults.html", result=True, end=False, artist=getcookie("artist"), username=getcookie("User"))
    else:
      addcookie("artist", name)
      if song.lower() in getalbumnames(name):
        if coverimagetobyte(getalbumcover(song, name)) == coverimagetobyte(getalbumcover(accsong, name)):
          points = points + 1
          if songnumber > 9:
            if username != False:
              addxp(username, points)
              addmoney(username, points)
              changealbumcoverscore(username, points*10, name.lower())
            return render_template("guessalbumresults.html", result=True, end=points*10, artist=getcookie("artist"), username=getcookie("User"))
          addcookie("albumnumber", songnumber)
          addcookie("points2", points)
          return render_template("guessalbumresults.html", result=True, end=False, artist=getcookie("artist"), username=getcookie("User"))
      if songnumber > 9:
        addxp(username, points)
        addmoney(username, points)
        changealbumcoverscore(username, points*10, name.lower())
        return render_template("guessalbumresults.html", result=accsong, end=points*10, artist=getcookie("artist"), username=getcookie("User"))
      addcookie("albumnumber", songnumber)
      addcookie("points2", points)
      return render_template("guessalbumresults.html", result=accsong, end=False, artist=getcookie("artist"), username=getcookie("User"))
  else:
    name = getcookie("artist")
    songnumber = getcookie("albumnumber")
    if songnumber == False:
      songnumber = 0
    points = getcookie("points2")
    if points == False:
      points = 0
    if name == False:
      return redirect("/")
    func = getrandomalbumcover(name)
    username = getcookie("User")
    delcookies()
    if username != False:
      addcookie("User", username)
    addcookie("album", func[1])
    addcookie("artist", name)
    addcookie("albumnumber", songnumber+1)
    addcookie("points2", points)
    return render_template("guessalbum.html", lyric=func[0], artist=name, songnumber=songnumber+1, points=points, username=getcookie("User"))