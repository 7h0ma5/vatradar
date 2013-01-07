from urllib.request import urlopen
from pymongo import MongoClient
import sys, time

DATA_SOURCE = "http://data.vattastic.com/vatsim-data.txt"
METAR_SOURCE = "ftp://tgftp.nws.noaa.gov/data/observations/metar/cycles/"
AIRPORT_SOURCE = "http://openflights.svn.sourceforge.net/viewvc/openflights/openflights/data/airports.dat"
AIRLINE_SOURCE = "http://openflights.svn.sourceforge.net/viewvc/openflights/openflights/data/airlines.dat"

conn = MongoClient('localhost', 27017)
db = conn.vatradar

def to_int(s):
    s = s.strip()
    return int(s) if s else 0

def download(url):
    print("downloading %s" % url)
    req = urlopen(url)
    return req.readlines()

def update_metar():
    cycle = time.strftime("%HZ.TXT", time.gmtime())
    data = download(METAR_SOURCE + cycle)
    for line in data:
        try:
            line = line.decode("utf-8").rstrip()
        except UnicodeDecodeError:
            continue

        if line[:1].isalpha():
            icao = line[0:4],
            data = {
                "icao": icao,
                "metar": line,
            }

            db.metar.update({"icao": icao}, {"$set": data}, True)
            print(icao, end="\r")

def atc(data):
    update = {
        "callsign": data[0],
        "cid": to_int(data[1]),
        "realname": data[2],
        "frequency": data[4],
        "position": [float(data[5]), float(data[6])],
        "server": data[14],
        "rating": data[16],
        "type": to_int(data[18]),
        "atis": data[35],
    }
    callsign = update["callsign"]
    db.atc.update({"callsign": callsign}, {"$set": update}, True)
    print(callsign, end="\r")

def pilot(data):
    update = {
        "callsign": data[0],
        "cid": to_int(data[1]),
        "realname": data[2],
        "position": [float(data[5]), float(data[6])],
        "altitude": to_int(data[7]),
        "speed": to_int(data[8]),
        "aircraft": data[9],
        "tas": to_int(data[10]),
        "origin": data[11],
        "flightlevel": data[12],
        "destination": data[13],
        "server": data[14],
        "squawk": to_int(data[17]),
        "deptime": to_int(data[22]),
        "remarks": data[29],
        "route": data[30],
        "heading": to_int(data[38]),
    }

    callsign = update["callsign"]
    db.pilots.update({"callsign": callsign}, {"$set": update}, True)
    print(callsign, end="\r")

def client(data):
    data = data.split(":")

    try:
        if data[3] == "PILOT": pilot(data)
        elif data[3] == "ATC": atc(data)
    except:
        print("something wrong with " + str(data))

def update_data():
    data = download(DATA_SOURCE)

    state = None
    for line in data:
        try:
            line = line.decode("iso-8859-1").rstrip()
        except UnicodeDecodeError:
            continue

        if line.startswith(";"):
            state = None
            continue
        elif line.startswith("!CLIENTS"):
            state = client
            continue

        if state:
            state(line)

def update_airlines():
    data = download(AIRLINE_SOURCE)

    for line in data:
        try:
            line = line.decode("iso-8859-1")
        except UnicodeDecodeError:
            continue

        data = line.split(",")
        if len(data) < 7: continue

        update = {
            "name": data[1].strip('"'),
            "icao": data[4].strip('"'),
            "rtf": data[5].strip('"'),
            "country": data[6].strip('"'),
        }

        icao = update["icao"]
        if (len(icao) != 3): continue
        db.airlines.update({"icao": icao}, {"$set": update}, True)
        print(icao, end="\r")

def update_airports():
    data = download(AIRPORT_SOURCE)

    for line in data:
        try:
            line = line.decode("iso-8859-1")
        except UnicodeDecodeError:
            continue

        data = line.split(",")
        if len(data) < 9: continue
        try:
            update = {
                "name": data[1].strip('"'),
                "city": data[2].strip('"'),
                "country": data[3].strip('"'),
                "iata": data[4].strip('"'),
                "icao": data[5].strip('"'),
                "position": [float(data[6]), float(data[7])],
                "altitude": to_int(data[8]),
            }
        except ValueError:
            continue

        icao = update["icao"]
        if (len(icao) != 4): continue
        db.airports.update({"icao": icao}, {"$set": update}, True)
        print(icao, end="\r")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("no command specified")

    elif sys.argv[1] == "airports":
        update_airports()

    elif sys.argv[1] == "airlines":
        update_airlines()

    elif sys.argv[1] == "loop":
        while True:
            update_data()
            #update_metar()
            time.sleep(30)
