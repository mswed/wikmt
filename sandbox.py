import json
from pprint import pprint

with open("./static/data/wwtp_backup_data.json") as inp:
    states = set()
    data = json.load(inp)
    for record in data:
        states.add(record.get("wwtp_jurisdiction"))

    pprint(states)
