from flask import *
from processing import *
from iot_data import IotData
import pprint
import yaml
import json

app = Flask(__name__)

pp = pprint.PrettyPrinter(indent=4)

configFile = "config.yaml"

# /!\ A REMPLACER AVEC LES BONNES VALEURS /!\
with open(configFile, 'r') as f:
    docs = yaml.load(f)
    datastore = IotData(docs['ELASTICSEARCH_NODE'])

HTTP_BAD_REQUEST_STATUS_CODE = 400

granularities = ["year", "month", "day", "hour"]
types = ["in", "out"]
devices = ["mlx", "wifi", "flir", "other"]


def answer(message, status=200):
    resp = make_response(json.dumps(message), status)
    resp.mimetype="application/json"
    return resp


def is_int(i):
    try:
        int(i)
        return True
    except ValueError:
        return False



@app.route("/api/event", methods=["POST"])
def event():
    data = request.get_json()
    data = dict((k, v.lower() if isinstance(v, str) else v) for k, v in data.items())
    
    if not all(key in data for key in ("parking", "timestamp", "device", "type")):
        return answer({ "error": "Not all key are there! Abort..."}, HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer({ "error": "Parking is not numeric!"}, HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["timestamp"]):
        return answer({ "error": "Timestamp is not numeric!"}, HTTP_BAD_REQUEST_STATUS_CODE)

    if not data["device"] in devices:
        return answer({ "error": "Device is not a valid value! Abort...."}, HTTP_BAD_REQUEST_STATUS_CODE)

    if not data["type"] in types:
        return answer({ "error": "Type is not a valid value! Abort...."}, HTTP_BAD_REQUEST_STATUS_CODE)

    resp = datastore.add_event(data["parking"], data["timestamp"] * 1000, data["device"], data["type"])

    return answer({
        "event_id": resp['_id']
    })


@app.route("/api/stat", methods=["GET"])
def stat():
    data = request.args
    data = dict((k, v.lower() if isinstance(v, str) else v) for k, v in data.items())

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("parking", "granularity", "from", "to")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    # if not data["granularity"] in granularities:
    #     return answer("Granularity is not a valid value! Abort....", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["from"]):
        return answer("From is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["to"]):
        return answer("To is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    resp = datastore.get_stats(int(data["parking"]), int(data["from"]), int(data["to"]), data["granularity"])

    if resp["timed_out"]:
        return answer({ "error" : "Query timed out ..." }, 500)

    stats = map(
        lambda bucket: {
            "time": bucket["key"] // 1000,
            "delta": bucket["delta"]["value"],
            "count": bucket["counter"]["value"]
        },
        resp["aggregations"]["by_interval"]["buckets"]
    )

    return answer(list(stats))


@app.route("/api/occupation", methods=["GET"])
def occupation():
    data = request.args
    data = dict((k, v.lower() if isinstance(v, str) else v) for k, v in data.items())

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ["parking"]):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    r = cassandra_req("SELECT occupation FROM park_occupation WHERE parking = " + str(data["parking"]) + ";")

    return answer('{"vehicule" : ' + str(len(r)) + '}')


@app.route("/api/vehicule", methods=["GET"])
def vehicule():
    data = request.args
    data = dict((k, v.lower() if isinstance(v, str) else v) for k, v in data.items())

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("parking", "from", "to")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["from"]):
        return answer("from is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["to"]):
        return answer("to is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    r = cassandra_req("SELECT vehicle_id FROM events WHERE parking = " + str(data["parking"]) + " allow filtering;")

    return answer("All data are well formatted! Processing data...")


@app.route("/api/parktime", methods=["GET"], defaults={"id": None})
@app.route("/api/parktime/<id>", methods=["GET"])
def parktime(id):
    data = request.args
    data = dict((k, v.lower() if isinstance(v, str) else v) for k, v in data.items())

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

    r = cassandra_req("SELECT timestamp, type FROM events WHERE vehicle_id = " + str(data["id"]) + "parking = " + str(data["parking"]) + "timestamp >= " + str(data["from"]) + " AND timestamp <= " + str(data["to"]) + ";")

    #r = process_vehicle(r, data["granularity"])

    park = json.dumps(r, sort_keys=True, separators=(',', ': '))

    return answer(park)


@app.route("/api/inout", methods=["GET"], defaults={"id": None})
@app.route("/api/inout/<id>", methods=["GET"])
def inout(id):
    data = request.args
    data = dict((k, v.lower() if isinstance(v, str) else v) for k, v in data.items())

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

    r = cassandra_req("SELECT timestamp, type FROM events WHERE vehicle_id = " + str(data["id"]) + "parking = " + str(data["parking"]) + "timestamp >= " + str(data["from"]) + " AND timestamp <= " + str(data["to"]) + ";")

    r = process_inout(r, data["granularity"])

    inout = json.dumps(r, sort_keys=True, separators=(',', ': '))

    return answer(inout)

@app.route("/", methods=["GET"])
def root():
    return answer("OK") 


if __name__ == "__main__":
    app.run(debug=True)
