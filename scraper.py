"enabled": Truefrom base64 import b64encode
import requests
import json
import jwt
import sys
import csv
import time
from urllib.parse import urlparse, urlencode
from pathlib import Path
from multiprocessing.dummy import Pool as ThreadPool

from rich.console import Console
console = Console()

# config
OVP_PREFIX = 'https://appovptok.ovpobs.tv'
OCSI_PREFIX = 'https://appocsitok.ovpobs.tv'
API_KEY = 'OTk5NDQ2OjpvY3NpLWFwaXVzZXI='
API_SECRET = 'MzAyYTgwZDY2ZDcwMWI4MmQ5MzA2MGQ2OTJmYmFmNTViZmYzZDQ3Nzk1YjU0NjI5MjU0ZTFjMGYxZjE2NTY5ZTo6M2FkYTk0NDExODNmOTgyNWMwYWFiOTE2MmIwYzQxYWM='
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0 Olympics Scraper'

DATA_DIRECTORY = "./docs/data"

# to be filled in later
ACCESS_TOKEN = ""

# data
ORGANISATIONS = {}
DISCIPLINES = {}
INDIVIDUALS = {}

configurations = []

# stack/#312464
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def dumpJSONToFile(folder, filename, data):
    filename = f'{DATA_DIRECTORY}/raw/requests/{folder}/{filename}'
    pth = Path(filename)
    pth.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, 'w') as file:
        json.dump(data, file)

def apiRequest(url, params, returnJSON = True):
    url = OCSI_PREFIX + url
    req = requests.get(url, params = params, headers = {
        "x-obs-app-token": ACCESS_TOKEN,
        "User-Agent": USER_AGENT
    })
    if returnJSON:
        folder = urlparse(req.request.url).path
        paramsWithoutFields = dict( [(x,y) for x,y in params.items() if not x.startswith('fields[')] )
        filename = urlencode(paramsWithoutFields) + ".json"
        try:
            data = req.json()
        except:
            print(req.text)
        if "errors" in data:
            console.log("Errors in response:")
            console.log(data)
            console.log(url)
        dumpJSONToFile(folder, filename, data)
        return data
    return req.text

def paginatedApiRequest(url, params, pageSize = 999, includes = ["scraperNone"]):
    page = 0
    pages = 1

    data = []
    included = []

    # split the includes into chunks of 3 - otherwise their servers crash
    includes = list(chunks(includes, 2))

    while (page != pages):
        page += 1
        for include in includes:
            # do not include anything
            if include == ["scraperNone"]:
                paginatedRequest = apiRequest(url, {
                    "page[size]": pageSize,
                    "page[number]": page,
                    **params
                })
            else:
                paginatedRequest = apiRequest(url, {
                    "page[size]": pageSize,
                    "page[number]": page,
                    "include": ','.join(include),
                    **params
                })
            paginationInfo = paginatedRequest["meta"]["pagination"]
            data.extend(paginatedRequest["data"])
            if "included" in paginatedRequest:
                included.extend(paginatedRequest["included"])
            page = paginationInfo["page"]
            pages = paginationInfo["pages"]
            # api returns 0 if there's only 1 page - bit of a hack to fix it
            if pages == 0: pages += 1
            if page == 0: page += 1
            percent = page / pages * 100
            console.log(f"'{url}' | {include} | Page {page:03d} of {pages:03d} downloaded | {round(percent, 3)}%")
    return {
        "data": data,
        "included": included
    }

with console.status("Signing in..."):
    identityRequest = requests.get(OVP_PREFIX + "/api/identity/app/token", params = {
        "api_key": API_KEY,
        "api_secret": API_SECRET,
    }, headers = {
        "x-obs-app-token": ACCESS_TOKEN,
        "User-Agent": USER_AGENT
    })

    ACCESS_TOKEN = identityRequest.text

    try:
        user = jwt.decode(ACCESS_TOKEN, options={"verify_signature": False})
        console.log(f"Signed in as: {user['username']} ({user['email']})")
    except:
        console.log("Incorrect credentials.")
        sys.exit(1)

def getApiCallFunction(url, params, pageSize = 1000, includes = ["scraperNone"]):
    def callApi():
        apireq = paginatedApiRequest(url, params, pageSize = pageSize, includes = includes)
    return callApi

def getEventsLoop():
    def callApi():
        def downloadEventUSDFMessages(event):
            eventId = event["id"]
            usdfData = apiRequest(f"/api/sports/events/{eventId}/usdf-message-ids", {
                "filter[messageTypes]": ','.join(
                    ["awards", "cumulative", "unit", "phase", "photofinish", "duration", "miscellaneous", "extended", "stats", "positioning"]
                )
            })["data"]
            for usdfMessage in usdfData:
                messageId = usdfMessage["id"]
                messageUrl = f"{OVP_PREFIX}/data/sports/usdf/v2/{messageId}.json"
                messageRequest = requests.get(messageUrl)
                if messageRequest.text == "Not found": continue
                filename = f'{DATA_DIRECTORY}/raw/usdf_messages/{messageId}.json'
                pth = Path(filename)
                pth.parent.mkdir(parents=True, exist_ok=True)
                with open(filename, 'w') as file:
                    file.write(messageRequest.text)
            console.log(f'USDF messages for event "{eventId}" downloaded ({event["attributes"]["name"]})')

        events = paginatedApiRequest("/api/events", {
            "fields[Event]": "createdAt,extendedInfo,externalId,isLive,medalsAmount,name,publishedAt,resultsAmount,rsc,sportClasses,competitors,discipline,medals,stages"
        })["data"]

        pool = ThreadPool(8)
        messages = pool.map(downloadEventUSDFMessages, events)

        # Close the pool and wait for the work to finish
        pool.close()
        pool.join()
    return callApi

# yes it's verbose - it has to be otherwise the data can't be linked together
tasks = [{
    "name": "Download countries",
    "func": getApiCallFunction("/api/organisations", {
        "fields[Organisation]": "createdAt,description,extendedInfo,externalId,jaSortOrder,localName,name,nameVariations,publishedAt,statistics,updatedAt,country,flag,medalCounts,participants"
    }),
    "enabled": True
}, {
    "name": "Download participants",
    "func": getApiCallFunction("/api/participants", {
        "fields[Participant]": "createdAt,extendedInfo,externalId,individualParticipantType,name,participantType,statistics,tvFamilyName,tvInitialName,tvTeamName,updatedAt,children,competitors,discipline,individual,organisation,parents"
    }),
    "enabled": True
}, {
    "name": "Download individuals",
    "func": getApiCallFunction("/api/individuals", {
        "fields[Individual]": "ambition,breed,clubName,coach,colour,countryOfBirth,createdAt,dateOfBirth,education,extendedInfo,externalId,gender,generalBiography,generalBiographyPlain,groom,height,hero,hobbies,individualType,name,nationality,nickname,occupation,otherSports,owner,passport,placeOfBirth,preferredFamilyName,preferredGivenName,profileImages,publishedAt,secondOwner,sex,sire,sportingDebut,startedCompeting,updatedAt,weight,participants,profileImage,thumbnail"
    }, pageSize = 100),
    "enabled": True
}, {
    "name": "Download events and USDF messages",
    "func": getEventsLoop(),
    "enabled": True
}, {
    "name": "Download event-units",
    "func": getApiCallFunction("/api/event-units", {
    # timelineMarker should be in here but apparently the "relationship does not exist"
    "fields[EventUnit]": "competitionDate,createdAt,end,extendedInfo,externalId,publishedAt,rsc,scheduleStatus,start,title,updatedAt,competitors,highlightVod,medals,phase,results,scheduleItems,subEventUnits,venue"
    },),
    "enabled": True
}, {
    "name": "Download sub-event-units",
    "func": getApiCallFunction("/api/sub-event-units", {
    "fields[SubEventUnit]": "competitionDate,createdAt,end,extendedInfo,externalId,publishedAt,rsc,scheduleStatus,start,title,updatedAt,competitors,eventUnit,medals,results,scheduleItems,venue"
    }, pageSize = 100),
    "enabled": True
}, {
    "name": "Download stages",
    "func": getApiCallFunction("/api/stages", {
        "fields[Stage]": "brackets,createdAt,extendedInfo,externalId,publishedAt,rsc,stageType,title,updatedAt,competitors,event,phases"
    }, pageSize = 100),
    "enabled": True
}, {
    "name": "Download phases",
    "func": getApiCallFunction("/api/phases", {
        "fields[Phase]": "createdAt,extendedInfo,externalId,publishedAt,rsc,scheduleStatus,title,updatedAt,competitors,eventUnits,highlightVod,scheduleItems,stage"
    }),
    "enabled": True
}, {
    "name": "Download competitors",
    "func": getApiCallFunction("/api/competitors", {
        "fields[Competitor]": "createdAt,extendedInfo,externalId,name,order,paraClass,publishedAt,rsc,updatedAt,event,eventUnit,medals,participant,phase,results,scheduleSession,stage,subEventUnit"
    }),
    "enabled": True
}, {
    "name": "Download medals",
    "func": getApiCallFunction("/api/medals", {
        "fields[Medal]": "createdAt,description,determinedDate,extendedInfo,externalId,medalType,perpetual,publishedAt,rsc,updatedAt,competitor,discipline,event,eventUnit,organisation,participant,subEventUnit"
    }, 100),
    "enabled": True
}, {
    "name": "Download venues",
    "func": getApiCallFunction("/api/venues", {
        "fields[Venue]": "coordinates,country,createdAt,description,extendedInfo,externalId,isSportVenue,keyFacts,localName,location,name,publishedAt,updatedAt,venueType,children,disciplines,headerImage,map,parent,scheduleItems,scheduleSessions"
    }, 100),
    "enabled": True
}, {
    "name": "Download schedule-sessions",
    "func": getApiCallFunction("/api/schedule-sessions", {
        "fields[ScheduleSession]": "action,awardIndicator,broadcastEnd,broadcastPublished,broadcastStart,broadcastUnpublished,code,competitionDate,coverageEnd,coverageStart,createdAt,disciplineCode,end,eventSession,eventSessionEnd,eventSessionStart,eventUnitCount,extendedInfo,externalId,integrated,isHidden,live,phaseCount,playbackUrl,publishedAt,raceDataOnly,runDownTime,runUpTime,scheduleItemCount,sessionType,start,state,superSession,title,unilateral,updatedAt,videoFeed,videoId,activeScheduleItems,channel,commentaries,disciplines,events,ferVod,fieldsOfPlay,highlightVod,organisations,participants,scheduleItems,shortFormVods,stream,tags,thumbnail,venue"
    }),
    "enabled": True
}, {
    "name": "Download schedule-items",
    "func": getApiCallFunction("/api/schedule-items", {
        "fields[ScheduleItem]": "awardClass,awardSubClass,competitionDate,createdAt,end,endType,extendedInfo,externalId,hideEndDate,hideStartDate,isActive,isHidden,order,publishedAt,scheduleItemType,sessionCode,start,startType,status,subtype,title,updatedAt,disciplines,eventUnits,events,organisations,participants,phases,precedingSibling,scheduleSession,stages,subEventUnits,venue"
    }, 100),
    "enabled": True
}, {
    "name": "Download ceremonies",
    "func": getApiCallFunction("/api/ceremonies", {
        "fields[Ceremony]": "createdAt,externalId,name,publishedAt,updatedAt,pictogram"
    }, 100),
    "enabled": True
}, {
    "name": "Download medal-counts",
    "func": getApiCallFunction("/api/medal-counts", {
        "fields[MedalCount]": "bronze,createdAt,gold,goldRank,publishedAt,silver,total,totalRank,updatedAt,discipline,organisation"
    }, 100),
    "enabled": True
}, {
    "name": "Download aggregates",
    "func": getApiCallFunction("/api/aggregates", {
        "fields[Aggregate]": "aggregateType,createdAt,key,publishedAt,updatedAt,value,discipline,organisation,tags"
    }, 100),
    "enabled": True
}, {
    "name": "Download disciplines",
    "func": getApiCallFunction("/api/disciplines", {
        "fields[Discipline]": "createdAt,description,eventCount,extendedInfo,externalId,federationLabel,federationLink,isFeatured,isNew,jaSortOrder,name,publishedAt,rsc,statistics,updatedAt,events,organisations,participants,pictogram,scheduleSessions,thumbnail"
    }, 100),
    "enabled": True
}, {
    "name": "Download results",
    "func": getApiCallFunction("/api/results", {
        "fields[Result]": "against,createdAt,diff,extendedInfo,externalId,externalRowKeyList,for,frameId,ingestOrganisation,irm,lost,penalty,played,pool,publishedAt,qualificationMark,rank,rankEqual,ratio,resultType,rsc,sortOrder,status,tied,title,totalValue,universalIdsList,updatedAt,value,valueType,wlt,won,children,competitor,parent,records"
    }, 100),
    "enabled": True
}]

pool = ThreadPool(12)

def runTask(task):
    if not task["enabled"]: return
    console.log(f"Task '{task['name']}' started.")
    task["func"]()
    console.log(f"Task '{task['name']}' accomplished.")

pool.map(runTask, tasks)
