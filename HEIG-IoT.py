#import logging
from flask import *
import pprint
from flask_cassandra import CassandraCluster

app = Flask(__name__)
cassandra = CassandraCluster()

# /!\ A REMPLACER AVEC LES BONNES VALEURS /!\
app.config['CASSANDRA_NODES'] = ['cassandra-c1.terbiumlabs.com']

pp = pprint.PrettyPrinter(indent=4)

granularities = ["year", "month", "day", "hour"]


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

@app.route("/cassandra_test")
def cassandra_test():
    session = cassandra.connect()
    session.set_keyspace("monty_python")
    cql = "SELECT * FROM sketches LIMIT 1"
    r = session.execute(cql)
    return str(r[0])

@app.route('/api/event', methods=['POST'])
def event():
    # - timestamp[int]
    # - type[enum( in / out)]
    # - id[string](hash)
    data = request.get_json()
    # Timestamps, type d'event (compter les véhicule ou durée de session), parking, Donnée pour cette event (Entrée/sortie, id client)
    if data is None:
        return "This is None"
    else:
        return pp.pformat(data)


@app.route('/api/stat', methods=['GET'])
def stat():
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("granularity", "from", "to", "parking")):
        return answer("Not all key are there! Abort...", 400)

    if not data['granularity'] in granularities:
        return answer("Granularity is not a valid value! Abort....", 400)

    if not is_int(data['parking']):
        return answer("Parking is not numeric!", 400)

    if not is_int(data['from']):
        return answer("From is not numeric!", 400)

    if not is_int(data['to']):
        return answer("To is not numeric!", 400)

    return answer("All data are well formatted! Processing data...")


@app.route('/api/occupation', methods=['GET'])
def occupation():
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("parking", "time")):
        return answer("Not all key are there! Abort...", 400)

    if not is_int(data['parking']):
        return answer("Parking is not numeric!", 400)

    if not is_int(data['time']):
        return answer("Time is not numeric!", 400)

    return answer("All data are well formatted! Processing data...")


@app.route('/api/parktime', methods=['GET'], defaults={'id': None})
@app.route('/api/parktime/<id>', methods=['GET'])
def parktime(id):
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("from", "to", "parking")):
        return answer("Not all key are there! Abort...", 400)

    if not is_int(data['parking']):
        return answer("Parking is not numeric!", 400)

    if not is_int(data['from']):
        return answer("From is not numeric!", 400)

    if not is_int(data['to']):
        return answer("To is not numeric!", 400)

    if id is None or id == "":
        return answer("ID is not here, getting for all vehicles!", 400)

    return answer("All data are well formatted! Processing data for vehicle " + id + "...")


@app.route('/api/inout', methods=['GET'], defaults={'id': None})
@app.route('/api/inout/<id>', methods=['GET'])
def inout(id):
    data = request.args

    print("Received data!\n" + pp.pformat(data))

    if not all(key in data for key in ("from", "to", "parking")):
        return answer("Not all key are there! Abort...", 400)

    if not is_int(data['parking']):
        return answer("Parking is not numeric!", 400)

    if not is_int(data['from']):
        return answer("From is not numeric!", 400)

    if not is_int(data['to']):
        return answer("To is not numeric!", 400)

    if id is None or id == "":
        return answer("ID is not here, getting for all vehicle!", 400)

    return answer("All data are well formatted! Processing data for vehicle " + id + "...")


if __name__ == '__main__':
    app.run(debug=True)
