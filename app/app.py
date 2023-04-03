from flask import Flask, render_template, send_from_directory
import fileinput
from itertools import cycle
import json

fi = cycle(fileinput.FileInput(["/home/davis/Developer/Work/CSUDC/methane/data"]))

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/data")
def get_data():
    data = json.loads(next(fi).strip())

    return data

@app.route('/static/<path:path>')
def server_static(path):
    return send_from_directory('static', path)
