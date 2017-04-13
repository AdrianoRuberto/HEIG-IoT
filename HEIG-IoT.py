from flask import *
import pprint

app = Flask(__name__)

pp = pprint.PrettyPrinter(indent=4)


@app.route('/', methods=['POST'])
def hello_world():
    data = request.get_json()
    if data is None:
        return "This is None"
    else:
        return pp.pformat(data)


if __name__ == '__main__':
    app.run(debug=True)
