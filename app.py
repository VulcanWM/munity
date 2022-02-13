from flask import Flask, render_template, request, redirect, send_file
from functions import getrandomline, addcookie, delcookies, getcookie, makeaccount, gethashpass, getuser
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
      addcookie("artist", name)
      if songnumber > 19:
        return render_template("guesssongresults.html", result=True, end=points*5, artist=getcookie("artist"), username=getcookie("User"))
      addcookie("songnumber", songnumber)
      addcookie("points", points + 1)
      return render_template("guesssongresults.html", result=True, end=False, artist=getcookie("artist"), username=getcookie("User"))
    else:
      addcookie("artist", name)
      if songnumber == 20:
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
    return render_template("signup.html")
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
      return render_template("signup.html", error=func)

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
    return render_template("login.html")
  else:
    return redirect("/")

@app.route("/login", methods=['POST', 'GET'])
def loginfunc():
  if request.method == 'POST':
    if getcookie("User") != False:
      return render_template("login.html", error="You have already logged in!")
    username = request.form['username']
    if getuser(username) == False:
      return render_template("login.html", error="That is not a username!")
    password = request.form['password']
    if check_password_hash(gethashpass(username), password) == False:
      return render_template("login.html", error="Wrong password!")
    addcookie("User", username)
    return redirect("/")
  else:
    return redirect("/")