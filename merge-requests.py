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

def getJSONFromFile(folder, filename):
    filename = f'{DATA_DIRECTORY}/raw/requests/{folder}/{filename}'
    console.log(f"Loading {filename}")
    with open(filename, 'r') as file:
        fileData = file.read()
        console.log("parsing json")
        jsonData = json.loads(fileData)
        return jsonData

def apiRequest(url, params, returnJSON = True):
    url = OCSI_PREFIX + url
    folder = urlparse(url).path
    paramsWithoutFields = dict( [(x,y) for x,y in params.items() if not x.startswith('fields[')] )
    filename = urlencode(paramsWithoutFields) + ".json"
    return getJSONFromFile(folder, filename)

def paginatedApiRequest(url, params, pageSize = 1000, includes = ["scraperNone"]):
    page = 0
    pages = 1

    data = []
    included = []

    while (page != pages):
        page += 1
        for include in includes:
            paginatedRequest = apiRequest(url, {
                "page[size]": pageSize,
                "page[number]": page,
                **params
            })
            paginationInfo = paginatedRequest["meta"]["pagination"]
            data.extend(paginatedRequest["data"])
            page = paginationInfo["page"]
            pages = paginationInfo["pages"]
            # api returns 0 if there's only 1 page - bit of a hack to fix it
            if pages == 0: pages += 1
            if page == 0: page += 1
            percent = page / pages * 100
    return data

def getApiCallFunction(url, params, pageSize = 1000, includes = ["scraperNone"]):
    def callApi():
        apireq = paginatedApiRequest(url, params, pageSize = pageSize, includes = includes)
    return callApi

def dumpJSONToFile(requestId, data):
    filename = f'{DATA_DIRECTORY}/raw/merged_requests/{requestId}.json'
    pth = Path(filename)
    pth.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, 'w') as file:
        json.dump(data, file)

listData = {}
listData["aggregates"] = paginatedApiRequest('/api/aggregates', {}, 100)
listData["ceremonies"] = paginatedApiRequest('/api/ceremonies', {}, 100)
listData["competitors"] = paginatedApiRequest('/api/competitors', {}, 1000)
listData["disciplines"] = paginatedApiRequest('/api/disciplines', {}, 100)
listData["events"] = paginatedApiRequest('/api/events', {}, 999)
listData["event-units"] = paginatedApiRequest('/api/event-units', {}, 1000)
listData["individuals"] = paginatedApiRequest('/api/individuals', {}, 100)
listData["medal-counts"] = paginatedApiRequest('/api/medal-counts', {}, 100)
listData["medals"] = paginatedApiRequest('/api/medals', {}, 100)
listData["organisations"] = paginatedApiRequest('/api/organisations', {}, 1000)
listData["participants"] = paginatedApiRequest('/api/participants', {}, 1000)
listData["phases"] = paginatedApiRequest('/api/phases', {}, 1000)
listData["results"] = paginatedApiRequest('/api/results', {}, 100)
listData["schedule-items"] = paginatedApiRequest('/api/schedule-items', {}, 100)
listData["schedule-sessions"] = paginatedApiRequest('/api/schedule-sessions', {}, 1000)
listData["stages"] = paginatedApiRequest('/api/stages', {}, 100)
listData["sub-event-units"] = paginatedApiRequest('/api/sub-event-units', {}, 100)
listData["venues"] = paginatedApiRequest('/api/venues', {}, 100)

data = {}

for dataStreamId in listData:
    dataStream = listData[dataStreamId]
    console.log(f"Dumping {dataStreamId}")
    dumpJSONToFile(dataStreamId, listData[dataStreamId])
