from flask import Flask, render_template, request, redirect, send_file
from functions import getrandomline, addcookie, delcookies, getcookie
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

@app.route("/")
def index():
  return render_template("index.html", artist=getcookie("artist"))

@app.route("/setartist", methods=['POST', 'GET'])
def getartistfunc():
  if request.method == 'POST':
    name = request.form['artist']
    delcookies()
    addcookie("artist", name)
    return redirect("/")
  else:
    return render_template("setartist.html", artist=getcookie("artist"))

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
    delcookies()
    if song.lower() == accsong.lower():
      addcookie("artist", name)
      if songnumber > 19:
        return render_template("guesssongresults.html", result=True, end=points*5, artist=getcookie("artist"))
      addcookie("songnumber", songnumber)
      addcookie("points", points + 1)
      return render_template("guesssongresults.html", result=True, end=False, artist=getcookie("artist"))
    else:
      addcookie("artist", name)
      if songnumber == 20:
        return render_template("guesssongresults.html", result=accsong, end=points*5, artist=getcookie("artist"))
      addcookie("songnumber", songnumber)
      addcookie("points", points)
      return render_template("guesssongresults.html", result=accsong, end=False, artist=getcookie("artist"))
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
    delcookies()
    addcookie("song", func[0])
    addcookie("artist", name)
    addcookie("songnumber", songnumber+1)
    addcookie("points", points)
    return render_template("guesssong.html", lyric=func[1], artist=name, songnumber=songnumber+1, points=points)

@app.route("/sticky.js")
def scriptjs():
  return send_file("static/sticky.js")

@app.route('/main.css')
def maincss():
  return send_file("static/main.css")