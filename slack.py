import json

def process_payload(slack_payload):
    with open('example_payload.json', 'w') as outfile:
        json.dump(slack_payload, outfile)
    return
