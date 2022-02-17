from flask import Flask, request, Response
from threading import Thread
from time import time
import os

app = Flask(__name__)

@app.route("/", methods=['POST'])
def response():
    """Process Slack interactive message POST request"""
    def dump_payload(**kwargs):
        """Dump payload to JSON file"""
        from json import dump, loads
        payload = loads(kwargs.get('payload', {}))
        with open(os.path.join('/path/to/POST_DIR/', f'{time()}.json'), 'w+') as outfile:
            dump(payload, outfile)
        return
    if request.method == 'POST':
        # Process post request as thread to return 200 status code within 3 seconds
        thread = Thread(target=dump_payload, kwargs={'payload': request.values['payload']})
        thread.start()
        return Response(status=200)
    else:
        return Response(status=501)

