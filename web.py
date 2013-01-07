from bottle import route, run, request, abort, static_file
from pymongo import Connection
from bson import json_util
import bottle
import json

def jdumps(obj):
    return json.dumps(obj, default=json_util.default)

connection = Connection("localhost", 27017)
db = connection.vatradar

@route("/")
def index():
    return static_file("index.html", root="web/")

@route("/static/<filename:path>")
def index(filename):
    return static_file(filename, root="web/")

@route("/pilots/", method="GET")
def get_pilots():
    pilots = db.pilots.find({}, {"callsign": 1, "position": 1, "heading": 1, "speed": 1, "aircraft": 1})
    return jdumps([pilot for pilot in pilots])

@route("/pilots/:id", method="GET")
def get_pilot(id):
    pilot = db.pilots.find_one({"callsign": id})
    if not pilot:
        abort(404, 'No pilot with callsign %s' % id)
    return jdumps(pilot)

@route("/atc/", method="GET")
def get_atc():
    atc = db.atc.find({})
    return jdumps([a for a in atc])

run(host='0.0.0.0', port=8080, debug=True)
