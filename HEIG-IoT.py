from flask import *
from flask_cassandra import CassandraCluster
import pprint
import json
from processing import *

app = Flask(__name__)
cassandra = CassandraCluster()

# /!\ A REMPLACER AVEC LES BONNES VALEURS /!\
app.config['CASSANDRA_NODES'] = ['localhost']

pp = pprint.PrettyPrinter(indent=4)

HTTP_BAD_REQUEST_STATUS_CODE = 400

granularities = ["year", "month", "day", "hour"]
types = ["in", "out"]
devices = ["mlx", "wifi", "flir"]


def answer(message, status=200):
    if app.debug:
       print(message + "\nStatus: " + str(status))

    return make_response(message, status)


def is_int(i):
    try:
        int(i)

        return True
    except ValueError:
        return False


def cassandra_req(req):
    session = cassandra.connect()
    session.set_keyspace("data")
    r = session.execute(req)
    return list(r)


@app.route("/api/event", methods=["POST"])
def event():
    data = request.get_json()

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("parking", "timestamp", "device", "type", "id")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["timestamp"]):
        return answer("Timestamp is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not data["device"] in devices:
        return answer("Device is not a valid value! Abort....", HTTP_BAD_REQUEST_STATUS_CODE)

    if not data["type"] in types:
        return answer("Type is not a valid value! Abort....", HTTP_BAD_REQUEST_STATUS_CODE)

    req = "INSERT INTO events(\"event_id\", \"parking\", \"timestamp\", \"device\", \"type\", \"vehicle_id\") VALUES (uuid()," + str(data["parking"]) + "," + str(data["timestamp"]) + "," + "\'" + data["device"] + "\'" + "," + "\'" + data["type"] + "\'" + "," + "\'" + data["id"] + "\');"

    cassandra_req(req)

    return answer("All data are well formatted! Processing data...")


@app.route("/api/stat", methods=["GET"])
def stat():
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("parking", "granularity", "from", "to")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not data["granularity"] in granularities:
        return answer("Granularity is not a valid value! Abort....", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["from"]):
        return answer("From is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["to"]):
        return answer("To is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    r = cassandra_req("SELECT timestamp, count FROM park_stat WHERE parking = " + str(data["parking"]) + "timestamp >= " + str(data["from"]) + " AND timestamp <= " + str(data["to"]))

    if data["granularity"] == "day":
        r = process_day(r)  # 6h-18h

    if data["granularity"] == "month":
        r = process_day(r)  # 6h-18h
        r = process_month(r)  # 30 days

    if data["granularity"] == "year":
        r = process_day(r)  # 6h-18h
        r = process_month(r) # 30 days
        r = process_year(r)  # 365 days

    stats = json.dumps(r, sort_keys=True, separators=(',', ': '))

    return answer(stats)


@app.route("/api/occupation", methods=["GET"])
def occupation():
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("parking")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    r = cassandra_req("SELECT occ FROM park_occupation WHERE parking = " + str(data["parking"]))

    return answer('{"vehicule" : ' + str(r[0]) + '}')


@app.route("/api/vehicule", methods=["GET"])
def vehicule():
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("parking", "from", "to")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["from"]):
        return answer("from is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["to"]):
        return answer("to is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    r = cassandra_req("SELECT vehicle_id FROM events WHERE parking = " + str(data["parking"]))

    return answer("All data are well formatted! Processing data...")


@app.route("/api/parktime", methods=["GET"], defaults={"id": None})
@app.route("/api/parktime/<id>", methods=["GET"])
def parktime(id):
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("parking", "granularity", "from", "to")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not data["granularity"] in granularities:
        return answer("Granularity is not a valid value! Abort....", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["from"]):
        return answer("From is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["to"]):
        return answer("To is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if id is None or id == "":
        return answer("No vehicule ID!", HTTP_BAD_REQUEST_STATUS_CODE)

    r = cassandra_req("SELECT timestamp, type FROM events WHERE vehicle_id = " + str(data["id"]) + "parking = " + str(data["parking"]) + "timestamp >= " + str(data["from"]) + " AND timestamp <= " + str(data["to"]))

    #r = process_vehicle(r, data["granularity"])

    park = json.dumps(r, sort_keys=True, separators=(',', ': '))

    return answer(park)
    # return answer("All data are well formatted! Processing data for vehicle " + id + "...")


@app.route("/api/inout", methods=["GET"], defaults={"id": None})
@app.route("/api/inout/<id>", methods=["GET"])
def inout(id):
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("parking", "granularity", "from", "to")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not data["granularity"] in granularities:
        return answer("Granularity is not a valid value! Abort....", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["from"]):
        return answer("From is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["to"]):
        return answer("To is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if id is None or id == "":
        return answer("No vehicule ID!", HTTP_BAD_REQUEST_STATUS_CODE)

    r = cassandra_req("SELECT timestamp, type FROM events WHERE vehicle_id = " + str(data["id"]) + "parking = " + str(data["parking"]) + "timestamp >= " + str(data["from"]) + " AND timestamp <= " + str(data["to"]))

    r = process_inout(r, data["granularity"])

    inout = json.dumps(r, sort_keys=True, separators=(',', ': '))

    return answer(inout)


if __name__ == "__main__":
    app.run(debug=True)
