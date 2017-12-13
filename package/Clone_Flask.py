from flask import Flask, request
from .Test_Process import TestProcess

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World! my'

@app.route('/clone', methods=['POST', 'GET'])
def clone():
    cases = request.args.get("cases")
    timestamp = request.args.get("timestamp")
    if "," in cases:
        list_case = cases.split(',')
    else:
        list_case = [cases]
    if list_case or timestamp:
        TestProcess(list_case, timestamp)
    return "running"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
