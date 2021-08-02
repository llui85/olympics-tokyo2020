from base64 import b64encode
import requests
import json
import jwt
import sys

from rich.console import Console
console = Console()

# config
authPrefix = 'https://appovptok.ovpobs.tv'
appPrefix = 'https://appocsitok.ovpobs.tv'
API_KEY = 'OTk5NDQ2OjpvY3NpLWFwaXVzZXI='
API_SECRET = 'MzAyYTgwZDY2ZDcwMWI4MmQ5MzA2MGQ2OTJmYmFmNTViZmYzZDQ3Nzk1YjU0NjI5MjU0ZTFjMGYxZjE2NTY5ZTo6M2FkYTk0NDExODNmOTgyNWMwYWFiOTE2MmIwYzQxYWM='

# to be filled in later
ACCESS_TOKEN = ""
SDW_ENDPOINT = ""

configurations = []

def apiRequest(url, params, returnJSON = True):
    url = appPrefix + url
    req = requests.get(url, params = params, headers = {
        "x-obs-app-token": ACCESS_TOKEN,
    })
    if returnJSON:
        return req.json()
    return req.text

with console.status("Signing in..."):
    identityRequest = requests.get(authPrefix + "/api/identity/app/token", params = {
        "api_key": API_KEY,
        "api_secret": API_SECRET
    }, headers = {
        "x-obs-app-token": ACCESS_TOKEN,
    })

    ACCESS_TOKEN = identityRequest.text

    try:
        user = jwt.decode(ACCESS_TOKEN, options={"verify_signature": False})
        console.log(f"Signed in as: {user['username']} ({user['email']})")
    except:
        console.log("Incorrect credentials.")
        sys.exit(1)

# console.log(apiRequest("/api/widgets"))

with console.status("Downloading configuration..."):
    configItems = apiRequest("/api/configurations", {
        "fields[Configuration]": "key,value",
        "filter": json.dumps([{
            "name": "key",
            "op": "eq",
            "val": "sports-data-configuration"
        }])
    })
    for configItem in configItems['data']:
        if configItem["attributes"]["key"] == "sports-data-configuration":
            SDW_ENDPOINT = configItem["attributes"]["value"]["sdwEndpoint"]
            SDW_ENDPOINT = f"https://{SDW_ENDPOINT}"
