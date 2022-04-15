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
        ts = kwargs.get('ts', {}) # Filename is timestamp of initial POST request processing
        with open(os.path.join('POST', f'{ts}.json'), 'w+') as outfile:
            dump(payload, outfile)
        return
    if request.method == 'POST':
        ts = time() # Get timestamp before starting thread to preserve order
        thread = Thread( # Must return 200 in < 3 secs so process as thread
            target=dump_payload, 
            kwargs={
                'payload': request.values['payload'], 
                'ts': ts
            }
        )
        thread.start()
        return Response(status=200)
    else:
        return Response(status=501)

