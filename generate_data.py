import ujson as json
from urllib.parse import urlparse, urlencode
from pathlib import Path

from rich.console import Console
console = Console()

# config
OVP_PREFIX = 'https://appovptok.ovpobs.tv'
OCSI_PREFIX = 'https://appocsitok.ovpobs.tv'
API_KEY = 'OTk5NDQ2OjpvY3NpLWFwaXVzZXI='
API_SECRET = 'MzAyYTgwZDY2ZDcwMWI4MmQ5MzA2MGQ2OTJmYmFmNTViZmYzZDQ3Nzk1YjU0NjI5MjU0ZTFjMGYxZjE2NTY5ZTo6M2FkYTk0NDExODNmOTgyNWMwYWFiOTE2MmIwYzQxYWM='
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0 Olympics Scraper'

DATA_DIRECTORY = "./docs/data"

def getMergedJSON(dataStreamId):
    filename = f'{DATA_DIRECTORY}/raw/merged_requests/{dataStreamId}.json'
    with open(filename, 'r') as file:
        fileData = file.read()
        console.log("parsing json")
        jsonData = json.loads(fileData)
        console.log("parsing done")
        return jsonData

def dumpJSONToFile(dataStreamId, data):
    filename = f'{DATA_DIRECTORY}/raw/merged_requests/{dataStreamId}.json'
    pth = Path(filename)
    pth.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, 'w') as file:
        json.dump(data, file)

mergedData = {}
mergedData["aggregates"] = getMergedJSON('aggregates')
mergedData["ceremonies"] = getMergedJSON('ceremonies')
mergedData["competitors"] = getMergedJSON('competitors')
mergedData["disciplines"] = getMergedJSON('disciplines')
mergedData["events"] = getMergedJSON('events')
mergedData["event-units"] = getMergedJSON('event-units')
mergedData["individuals"] = getMergedJSON('individuals')
mergedData["medal-counts"] = getMergedJSON('medal-counts')
mergedData["medals"] = getMergedJSON('medals')
mergedData["organisations"] = getMergedJSON('organisations')
mergedData["participants"] = getMergedJSON('participants')
mergedData["phases"] = getMergedJSON('phases')
mergedData["results"] = getMergedJSON('results')
mergedData["schedule-items"] = getMergedJSON('schedule-items')
mergedData["schedule-sessions"] = getMergedJSON('schedule-sessions')
mergedData["stages"] = getMergedJSON('stages')
mergedData["sub-event-units"] = getMergedJSON('sub-event-units')
mergedData["venues"] = getMergedJSON('venues')

data = {}

for dataStreamId in mergedData:
    dataStream = mergedData[dataStreamId]
    console.log(f"Combining {dataStreamId}")
    for item in dataStream:
        if not item["type"] in data:
            data[item["type"]] = {}
        data[item["type"]][item["id"]] = item

dumpJSONToFile("all-by-type", data)

# for orgId in data["Organisation"]:
    # print(data["Organisation"][orgId]["attributes"])
