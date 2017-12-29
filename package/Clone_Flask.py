from flask import Flask, request
from Test_Process import TestProcess


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/clone', methods=['POST', 'GET'])
def clone():
    return api_test()

def api_test():
    cases = request.args.get("cases")
    timestamp = request.args.get("timestamp")
    if cases or timestamp:
        if "," in cases:
            list_case = cases.split(',')
        else:
            list_case = [cases]
        TestProcess(list_case, timestamp)
        return "running test!!......"
    else:
        return "参数不正确!!!"


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', threaded=True)
