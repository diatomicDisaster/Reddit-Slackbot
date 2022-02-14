# Running on port 8080
from flask import Flask, request, Response
from threading import Thread
import json
import sys
from slack import process_payload
# from flask_reverse_proxy_fix.middleware import ReverseProxyPrefixFix

app = Flask(__name__)

# app.config['REVERSE_PROXY_PATH'] = '/'
# ReverseProxyPrefixFix(app)

# @app.route("/")
# def hello():
#     return "Hello world! This is a bad test."

@app.route("/", methods=['POST', 'GET'])
def response():
    def interact(slack_payload):
        from slack import process_payload
        process_payload(slack_payload)
        return
    if request.method == 'POST':
        slack_payload = json.loads(request.values['payload'])
        #thread = Thread(target=interact, kwargs={'slack_payload': slack_payload})
        #thread.start()
        process_payload(slack_payload)
        return Response(status=200)
    else:
        return "Unrecognised request"


# if __name__ == '__main__':
#     app.run()
