from flask import *
import pprint
from flask_cassandra import CassandraCluster

app = Flask(__name__)
cassandra = CassandraCluster()

# /!\ A REMPLACER AVEC LES BONNES VALEURS /!\
app.config['CASSANDRA_NODES'] = ['cassandra-c1.terbiumlabs.com']

pp = pprint.PrettyPrinter(indent=4)

HTTP_BAD_REQUEST_STATUS_CODE = 400

granularities = ["year", "month", "day", "hour"]
types = ["in", "out"]


def answer(message, status=200):
    #if app.debug:
    #    print(message + "\nStatus: " + str(status))

    return make_response(message, status)


def is_int(i):
    try:
        int(i)

        return True
    except ValueError:
        return False

@app.route("/cassandra_test")
def cassandra_test():
    session = cassandra.connect()
    session.set_keyspace("monty_python")
    cql = "SELECT * FROM sketches LIMIT 1"
    r = session.execute(cql)
    return str(r[0])

@app.route("/api/event", methods=["POST"])
def event():
    data = request.get_json()

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("parking", "timestamp", "type", "id")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not data["type"] in types:
        return answer("Type is not a valid value! Abort....", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["timestamp"]):
        return answer("Timestamp is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    return answer("All data are well formatted! Processing data...")


@app.route("/api/stat", methods=["GET"])
def stat():
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("granularity", "from", "to", "parking")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not data["granularity"] in granularities:
        return answer("Granularity is not a valid value! Abort....", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["from"]):
        return answer("From is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["to"]):
        return answer("To is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    return answer("All data are well formatted! Processing data...")


@app.route("/api/occupation", methods=["GET"])
def occupation():
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("parking", "time")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["time"]):
        return answer("Time is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    return answer("All data are well formatted! Processing data...")


@app.route("/api/parktime", methods=["GET"], defaults={"id": None})
@app.route("/api/parktime/<id>", methods=["GET"])
def parktime(id):
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("from", "to", "parking")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["from"]):
        return answer("From is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["to"]):
        return answer("To is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if id is None or id == "":
        return answer("ID is not here, getting for all vehicles!", HTTP_BAD_REQUEST_STATUS_CODE)

    return answer("All data are well formatted! Processing data for vehicle " + id + "...")


@app.route("/api/inout", methods=["GET"], defaults={"id": None})
@app.route("/api/inout/<id>", methods=["GET"])
def inout(id):
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("from", "to", "parking")):
        return answer("Not all key are there! Abort...", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["parking"]):
        return answer("Parking is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["from"]):
        return answer("From is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if not is_int(data["to"]):
        return answer("To is not numeric!", HTTP_BAD_REQUEST_STATUS_CODE)

    if id is None or id == "":
        return answer("ID is not here, getting for all vehicle!", HTTP_BAD_REQUEST_STATUS_CODE)

    return answer("All data are well formatted! Processing data for vehicle " + id + "...")


if __name__ == "__main__":
    app.run(debug=True)
