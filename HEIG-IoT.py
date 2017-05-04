import logging
from flask import *
import pprint

app = Flask(__name__)

pp = pprint.PrettyPrinter(indent=4)

granularities = ["year", "month", "day", "hour"]


def answer(message, status=200):
    if app.debug:
        print(message + "\nStatus: " + str(status))
    return make_response(message, status)


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


@app.route('/api/stat', methods=['GET', 'POST'])
def stat():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return answer("Data are not JSON!", 400)

        print("Received data!\n" + pp.pformat(data))
        if not all(key in data for key in ("granularity", "from", "to")):
            return answer("Not all key are there! Abort...", 400)
        if not data['granularity'] in granularities:
            return answer("Granularity is not a valid value! Abort....", 400)
        if not isinstance(data['from'], int):
            return answer("From is not numeric!", 400)
        if not isinstance(data['to'], int):
            return answer("To is not numeric!", 400)
        return answer("All data are well formated! Processing data...")
    else:
        return answer("This is a GET")


if __name__ == '__main__':
    app.run(debug=True)
