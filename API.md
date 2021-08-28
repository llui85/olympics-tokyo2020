# API Documentation

# Work-in-progress docs for the (semi-official) olympics API used in the scraper.

This API has been reverse-engineered and is not endorsed by the IOC.

## API Basics
### Domains

The olympics API is hosted on various subdomains of `.ovpobs.tv`, and the main subdomains are `appovptok.ovpobs.tv` (authentication & udsf messages), and `appocsitok.ovpobs.tv` (to retrieve the actual data).

<details>
<summary>More information</summary>

The below list was extracted from the OVP SDK client. **Most** of them work the same - each channel generally has its own server.

For example, `ch7a-tok-prd` is the **production** server for **Channel 7 Australia** for the **Tokyo** olympics. In most cases, it's best to use the generic ones above as channel servers are often geolocked, or have slightly different configurations.

```js
{
	"ovp-tok-prd": "appovptok.ovpobs.tv",
	"obs-tok-prd": "appobstok.ovpobs.tv",
	"mm-tok-prd": "appmmtok.ovpobs.tv",
	"c1r-tok-prd": "appc1rtok.ovpobs.tv",
	"skyn-tok-prd": "appskyntok.ovpobs.tv",
	"imc-tok-prd": "appimctok.ovpobs.tv",
	"ocs-tok-prd": "appocstok.ovpobs.tv",
	"ocsi-tok-prd": "appocsitok.ovpobs.tv",
	"amxc-tok-prd": "appamxctok.ovpobs.tv",
	"vrt-tok-prd": "appvrttok.ovpobs.tv",
	"srg-tok-prd": "appsrgtok.ovpobs.tv",
	"em-tok-prd": "appemtok.ovpobs.tv",
	"ocsw-tok-prd": "appocswtok.ovpobs.tv",
	"yle-tok-prd": "appyletok.ovpobs.tv",
	"ch7a-tok-prd": "appch7atok.ovpobs.tv",
	"ovp-paratok-prd": "appovpparatok.ovpobs.tv",
	"obs-paratok-prd": "appobsparatok.ovpobs.tv",
	"ch4-paratok-prd": "appch4paratok.ovpobs.tv",
	"ipc-paratok-prd": "appipcparatok.ovpobs.tv",
	"ocst-paratok-prd": "appocstparatok.ovpobs.tv",
	"ocsi-paratok-prd": "appocsiparatok.ovpobs.tv",
	"ch7a-paratok-prd": "appch7aparatok.ovpobs.tv",
	"ovp-tok-acc": "appovptok-acceptance.ovpobs.tv",
	"obs-tok-acc": "appobstok-acceptance.ovpobs.tv",
	"mm-tok-acc": "appmmtok-acceptance.ovpobs.tv",
	"ovp-paratok-acc": "appovpparatok-acceptance.ovpobs.tv",
	"ovp-tst": "appovptok-testing.ovpobs.tv",
	"obs-tst": "appobstok-testing.ovpobs.tv",
	"mm-tst": "appmmtok-testing.ovpobs.tv",
	"ovp-zeus": "appovptok-testing-zeus.ovpobs.tv",
	"obs-zeus": "appobstok-testing-zeus.ovpobs.tv",
	"mm-zeus": "appmmtok-testing-zeus.ovpobs.tv",
	"ovp-apollo": "appovptok-testing-apollo.ovpobs.tv",
	"obs-apollo": "appobstok-testing-apollo.ovpobs.tv",
	"mm-apollo": "appmmtok-testing-apollo.ovpobs.tv",
	"ovp-dev": "appovptok-development.ovpobs.tv",
	"obs-dev": "appobstok-development.ovpobs.tv",
	"mm-dev": "appmmtok-development.ovpobs.tv"
}
```
</details>

### Authorisation

To authorise your requests to the app server, you will need to request an access token from the identity server. To send this, two parameters are required -  `api_key` and `api_secret`. These values can be scraped from a results page, or intercepted in the developer tools console. The credentials as of August 2021 are:

```py
API_KEY = '999446::ocsi-apiuser'
API_SECRET = '302a80d66d701b82d93060d692fbaf55bff3d47795b54629254e1c0f1f16569e::3ada9441183f9825c0aab9162b0c41ac'
```

Both values must be base64 encoded, then sent in as query parameters in a GET request to `/api/identity/app/token`.

```http
GET https://appovptok.ovpobs.tv/api/identity/app/token?api_key={base64(API_KEY)}&api_secret{base64(API_SECRET)}
```

The returned value from this endpoint is then sent in the header `x-obs-app-token`.

## Using the API

**Before using this data, it is highly recommended to read [section 2 of the ODF docs](https://odf.olympictech.org/2020-Tokyo/general/HTML/foundation/Foundation_Principles_body.htm#_Toc65756458), which is about how competitions are structured data-wise.**

Normally, it would be difficult to understand how the API works, and we'd have to resort to reverse engineering the JS client. Fortunately, [the type definition files for the API have been uploaded to GitHub](https://github.com/mediamonks/jsonapi-client/tree/master/examples/ovp/resources), which makes it much easier to understand. The only difference is a new endpoint `sub-event-units` (referenced in the ODF docs).

The API is a JSON:API server. Queries, filtering, including, sorting and pagination are comprehensively document in [the specification.](https://jsonapi.org/format/)

The data structure is complex, so the best way to get a feel for it is to run some queries yourself.

Try:
- getting the medal count for a country
- looking up an athlete by their surname (filter[])
- getting the list of events [and](https://jsonapi.org/format/#fetching-includes) their discipline
- getting the results for a particular heat for an event
- listing all the medals and who won them
- looking up what sessions were scheduled on a particular date
- getting a list of venues

If you're stuck (these docs are meant to be a starting point, not an official guide), try looking at the requests that the [web client](https://webocsiparatok.ovpobs.tv/olympic-family-iframe/?widget=results) makes.

**If you're still stuck, open an issue! I'm happy to help you if you're not sure how to get a particular bit of data**
